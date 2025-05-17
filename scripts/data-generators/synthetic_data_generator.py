"""
Reusable helper for data-generator scripts that use Semantic-Kernel +
Azure OpenAI. Handles environment loading, kernel wiring, prompt
registration and coloured logging.

Requires:
- semantic-kernel
- python-dotenv
- colorama
- pyyaml (if using YAML output in consuming scripts)
- azure-identity (if using Managed Identity for Azure OpenAI authentication)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Callable, Dict, List

import colorama
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig

class SyntheticDataGenerator:
    """
    A helper class to simplify the creation of synthetic data using Azure OpenAI
    and Semantic Kernel. It handles common setup tasks like environment variable
    loading, kernel initialization, logging, and prompt function creation.
    """

    def __init__(self, env_file_override: str = ".env", log_level: str = "INFO") -> None:
        """
        Initializes the SyntheticDataGenerator.

        Args:
            env_file_override (str): Path to a script-specific .env file to override
                                     general settings. Defaults to ".env".
            log_level (str): The logging level (e.g., "INFO", "DEBUG").
                             Defaults to "INFO".
        """
        colorama.init(autoreset=True)  # Initialize colorama for colored console output

        # Load environment variables from a general .env file and a specific override file
        load_dotenv()
        load_dotenv(env_file_override, override=True)

        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY") # Can be None

        if not self.azure_openai_endpoint or not self.azure_openai_deployment:
            raise EnvironmentError(
                "Azure OpenAI environment variables (AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_DEPLOYMENT) must be configured."
            )

        # Configure logging
        effective_log_level = os.getenv("LOG_LEVEL", log_level).upper()
        logging.basicConfig(
            level=effective_log_level, format="%(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("SyntheticDataGenerator initialized.")

        # Initialize Semantic Kernel
        self.kernel = self._create_kernel()
        self.logger.debug("Semantic Kernel initialized.")

    def _create_kernel(self) -> sk.Kernel:
        """Creates and configures a Semantic Kernel instance."""
        kernel = sk.Kernel()
        
        if self.azure_openai_api_key:
            self.logger.debug("Using API key for Azure OpenAI authentication.")
            service = AzureChatCompletion(
                deployment_name=self.azure_openai_deployment,
                endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_api_key,
                service_id="azure_open_ai",  # Unique identifier for the service
            )
        else:
            self.logger.debug("Using DefaultAzureCredential for Azure OpenAI authentication.")
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            service = AzureChatCompletion(
                deployment_name=self.azure_openai_deployment,
                endpoint=self.azure_openai_endpoint,
                ad_token_provider=token_provider,
                service_id="azure_open_ai",  # Unique identifier for the service
            )
            
        kernel.add_service(service)
        return kernel

    def create_prompt_function(
        self,
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
        Creates a Semantic Kernel prompt function from a template and registers it.

        Args:
            template (str): The prompt template string.
            function_name (str): The name for the kernel function.
            plugin_name (str): The name of the plugin to associate the function with.
            prompt_description (str): A description for the prompt function.
            input_variables (List[Dict[str, Any]]): A list of input variable
                                                     definitions for the prompt.
            max_tokens (int): The maximum number of tokens for the AI response.
            temperature (float): Controls randomness in the AI response. Defaults to 0.7.
            top_p (float): Controls nucleus sampling. Defaults to 0.95.

        Returns:
            Callable[..., str]: A synchronous function that can be called to execute
                                the prompt.
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

        kernel_function = self.kernel.add_function(
            function_name=function_name,
            plugin_name=plugin_name,
            prompt_template_config=prompt_config,
        )
        self.logger.debug(f"Prompt function '{plugin_name}.{function_name}' created.")

        async def _async_runner(**kwargs: Any) -> str:
            result = await self.kernel.invoke(kernel_function, **kwargs)
            return str(result)

        def sync_runner(**kwargs: Any) -> str:
            return asyncio.run(_async_runner(**kwargs))

        return sync_runner

