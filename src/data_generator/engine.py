from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Callable, Dict, List, Any, Final

import yaml
import colorama
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from data_generator.tool import DataGeneratorTool

__all__: list[str] = ["DataGenerator"]

_DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s %(levelname)-8s %(name)s :: %(message)s"
_LOGGER_NAME:        Final[str] = "data-generator"


class DataGenerator:  # pylint: disable=too-many-instance-attributes
    """
    Orchestrates end-to-end data generation.

    Parameters
    ----------
    tool:
        Concrete implementation of :class:`data_generator.tool.DataGeneratorTool`
        responsible for domain-specific prompt construction and post-processing.
    log_level:
        Logging verbosity passed straight to :pymod:`logging`.
    azure_openai_endpoint / azure_openai_deployment / azure_openai_api_key :
        Connection details for Azure OpenAI – can be provided as explicit
        arguments or via the corresponding environment variables.
    """

    def __init__(
        self,
        tool: "DataGeneratorTool",
        *,
        log_level: str | int = "INFO",
        azure_openai_endpoint: str | None = None,
        azure_openai_deployment: str | None = None,
        azure_openai_api_key: str | None = None,
    ) -> None:
        self.tool = tool
        load_dotenv()  # Load .env from CWD or parent (no error if missing)

        # ---- Resolve connection settings ---------------------------------
        self.azure_openai_endpoint: str | None = (
            azure_openai_endpoint
            or os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.azure_openai_deployment: str | None = (
            azure_openai_deployment
            or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        )
        self.azure_openai_api_key: str | None = (
            azure_openai_api_key
            or os.getenv("AZURE_OPENAI_API_KEY")
        )

        if not self.azure_openai_endpoint or not self.azure_openai_deployment:
            raise EnvironmentError(
                "Azure OpenAI connection details missing. "
                "Set --azure-openai-endpoint & --azure-openai-deployment CLI flags "
                "or AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT environment variables."
            )

        # --------------------------------------------------------------------- #
        # Logging configuration                                                 #
        # --------------------------------------------------------------------- #
        colorama.just_fix_windows_console()
        logging.basicConfig(format=_DEFAULT_LOG_FORMAT, level=log_level)
        self.logger: logging.Logger = logging.getLogger(_LOGGER_NAME)
        self.logger.debug(
            "Using Azure OpenAI endpoint '%s', deployment '%s'.",
            self.azure_openai_endpoint,
            self.azure_openai_deployment,
        )

        # --------------------------------------------------------------------- #
        # Semantic-Kernel initialisation                                        #
        # --------------------------------------------------------------------- #
        self.kernel: sk.Kernel = self._create_kernel()

    def _create_kernel(self) -> sk.Kernel:
        """
        Instantiate and return a Semantic-Kernel ``Kernel`` pre-configured with
        an ``AzureChatCompletion`` service instance.

        The method automatically selects authentication based on whether an
        explicit API key was supplied:
        - If ``self.azure_openai_api_key`` is set, that key is used.
        - Otherwise, a bearer token from ``DefaultAzureCredential`` is requested.

        Returns
        -------
        semantic_kernel.Kernel
            Fully initialised kernel ready to register prompt functions.
        """
        kernel = sk.Kernel()

        if self.azure_openai_api_key:
            self.logger.debug("Authenticating to Azure OpenAI with API key.")
            service = AzureChatCompletion(
                deployment_name=self.azure_openai_deployment,
                endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_api_key,
                service_id="azure_open_ai",
            )
        else:
            self.logger.debug("Authenticating to Azure OpenAI with DefaultAzureCredential.")
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            service = AzureChatCompletion(
                deployment_name=self.azure_openai_deployment,
                endpoint=self.azure_openai_endpoint,
                ad_token_provider=token_provider,
                service_id="azure_open_ai",
            )

        kernel.add_service(service)
        return kernel

    def create_prompt_function(  # noqa: PLR0913 (many params intentional)
        self,
        *,
        template: str,
        function_name: str,
        plugin_name: str,
        prompt_description: str,
        input_variables: List[Dict[str, Any]],
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> Callable[..., str]:
        """
        Register *template* as a Semantic-Kernel prompt function and return a
        synchronous wrapper that can be executed in a thread-pool.

        Parameters
        ----------
        template:
            The full prompt text (including any placeholders).
        function_name:
            Name of the function inside the plugin.
        plugin_name:
            Semantic-Kernel *plugin* (a logical grouping of functions).
        prompt_description:
            Short human-readable description used by SK.
        input_variables:
            List of dictionaries describing required template parameters.
        max_tokens:
            Maximum tokens to be generated by Azure OpenAI.
        temperature, top_p:
            Usual OpenAI sampling controls.

        Returns
        -------
        Callable[..., str]
            A blocking callable delegating to the underlying async SK runtime.
        """
        prompt_config = PromptTemplateConfig(
            name=function_name,
            description=prompt_description,
            template=template,
            input_variables=input_variables,
            execution_settings={
                "azure_open_ai": {  # Assuming "azure_open_ai" is the service_id
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                }
            },
        )

        # Register prompt and capture the resulting KernelFunction instance
        kernel_function = self.kernel.add_function(
            function_name=function_name,
            plugin_name=plugin_name,
            prompt_template_config=prompt_config,
        )
        self.logger.debug("Prompt function '%s.%s' created.", plugin_name, function_name)

        async def _async_runner(**kwargs: Any) -> str:
            """Async helper that forwards the call to ``kernel.invoke``."""
            result = await self.kernel.invoke(kernel_function, **kwargs)
            return str(result)

        def _sync_runner(**kwargs: Any) -> str:
            """Synchronous façade executed inside ``asyncio.to_thread``."""
            return asyncio.run(_async_runner(**kwargs))

        return _sync_runner

    # --------------------------------------------------------------------- #
    # Public façades                                                        #
    # --------------------------------------------------------------------- #
    def run(
        self,
        *,
        count: int,
        out_dir: Path,
        output_format: str = "json",
        concurrency: int = 8,
    ) -> None:
        """
        Blocking helper that delegates to the async implementation.

        Parameters
        ----------
        count:
            Number of records to generate.
        out_dir:
            Destination folder for the generated files.
        output_format:
            One of ``json``, ``yaml`` or ``txt``.
        concurrency:
            Upper bound on simultaneous Azure OpenAI requests.
        """
        asyncio.run(
            self._run_async(
                count=count,
                out_dir=out_dir,
                output_format=output_format,
                concurrency=concurrency,
            )
        )

    # --------------------------------------------------------------------- #
    # Async methods                                                         #
    # --------------------------------------------------------------------- #
    async def _run_async(
        self,
        *,
        count: int,
        out_dir: Path,
        output_format: str,
        concurrency: int,
    ) -> None:
        """
        Drive *count* asynchronous generation tasks while honouring
        *concurrency*.

        See Also
        --------
        _generate_one_async : Handles the life-cycle of a single record.
        """
        semaphore = asyncio.Semaphore(concurrency)
        tasks = [
            asyncio.create_task(
                self._generate_one_async(
                    index=i,
                    out_dir=out_dir,
                    output_format=output_format,
                    semaphore=semaphore,
                )
            )
            for i in range(1, count + 1)
        ]

        failures = 0
        for t in asyncio.as_completed(tasks):
            try:
                await t
            except Exception:  # pylint: disable=broad-exception-caught
                self.logger.exception("Generation task failed")
                failures += 1

        self.logger.info("Generation finished. Success: %s, Failed: %s", count - failures, failures)

    async def _generate_one_async(
        self,
        *,
        index: int,
        out_dir: Path,
        output_format: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """
        Generate, post-process, and persist a single record.

        Parameters
        ----------
        index :
            Ordinal number of the record being produced (1-based).
        out_dir :
            Target directory for the output file.
        output_format :
            File format - currently ``json``, ``yaml``, or plain text.
        semaphore :
            Synchronisation primitive controlling overall concurrency.
        """
        async with semaphore:
            prompt = self.tool.build_prompt(output_format)
            prompt_fn = self.create_prompt_function(
                template=prompt,
                function_name="generate",
                plugin_name=self.tool.toolName,
                prompt_description=f"{self.tool.toolName} generator",
                input_variables=[{"name": "index", "description": "record ordinal"}],
                max_tokens=2048,
            )
            raw_output: str = await asyncio.to_thread(prompt_fn, index=index)
            processed = self.tool.post_process(raw_output)

            await asyncio.to_thread(
                self._persist,
                index=index,
                data=processed,
                out_dir=out_dir,
                output_format=output_format,
            )
            self.logger.debug("Record %s generated.", index)

    # --------------------------------------------------------------------- #
    # Helper utilities                                                      #
    # --------------------------------------------------------------------- #
    def _persist(
        self,
        *,
        index: int,
        data: Any,
        out_dir: Path,
        output_format: str,
    ) -> None:
        """
        Persist **data** to disk using the requested *output_format*.

        Parameters
        ----------
        index:
            1-based ordinal used when naming the output file.
        data:
            Already post-processed object (dict / str / etc.).
        out_dir:
            Target directory. Created on-the-fly if it does not exist.
        output_format:
            ``json``, ``yaml``, ``txt`` or anything else supported by the
            default branch which falls back to ``str(data)``.
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / f"{index:04d}.{output_format}"

        if output_format == "json":
            with file_path.open("w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2)
        elif output_format == "yaml":
            with file_path.open("w", encoding="utf-8") as fp:
                yaml.safe_dump(data, fp, sort_keys=False)
        elif output_format == "txt":
            with file_path.open("w", encoding="utf-8") as fp:
                fp.write(str(data))
        else:  # default to plain text
            with file_path.open("w", encoding="utf-8") as fp:
                fp.write(str(data))

    # --------------------------------------------------------------------- #
    # Backwards-compat / simple sync loop (non-async)                       #
    # --------------------------------------------------------------------- #
    def generate_data(  # retained for compatibility; delegates to async path
        self,
        count: int,
        out_dir: Path,
        output_format: str = "json",
    ) -> None:
        """
        Backwards-compatibility shim calling :py:meth:`run`.

        Maintained for legacy scripts that expect a synchronous API.
        """
        self.run(
            count=count,
            out_dir=out_dir,
            output_format=output_format,
        )
