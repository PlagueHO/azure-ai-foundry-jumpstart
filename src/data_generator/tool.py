from __future__ import annotations

import argparse
import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Type

_logger = logging.getLogger(__name__)


class DataGeneratorTool(ABC):
    """
    Contract that every scenario-specific prompt builder must satisfy.

    Sub-classes should *only* embed domain logic (prompt templates, argument
    validation, post-processing) and have zero coupling to Azure / I/O.
    """

    # ------------------------------------------------------------------ #
    # Registry for dynamic discovery                                     #
    # ------------------------------------------------------------------ #
    _REGISTRY: ClassVar[Dict[str, Type["DataGeneratorTool"]]] = {}

    def __init_subclass__(cls, **kwargs):  # noqa: D401 (pylint)
        """Register every concrete subclass in the internal tool registry.

        This enables dynamic lookup/instantiation via `DataGeneratorTool.from_name`
        without requiring manual imports in the consumer code.
        """
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "name", None):
            raise AttributeError("DataGeneratorTool subclasses must define a unique `name` attribute.")
        if cls.name in cls._REGISTRY:
            raise ValueError(f"Duplicate tool registration for name '{cls.name}'.")
        cls._REGISTRY[cls.name] = cls
        _logger.debug("Registered DataGeneratorTool '%s' -> %s", cls.name, cls)

    # ------------------------------------------------------------------ #
    # Mandatory interface                                                #
    # ------------------------------------------------------------------ #
    name: str  # unique identifier (e.g. "tech-support")
    toolName: str  # Semantic Kernel tool name (e.g. "TechSupport"). Match: '^[0-9A-Za-z_]+$'

    @abstractmethod
    def build_prompt(self, output_format: str, *, unique_id: str | None = None) -> str:
        """Return the full prompt string for the given output format."""

    @abstractmethod
    def cli_arguments(self) -> List[Dict[str, Any]]:
        """
        Specification for CLI arguments consumed by this tool.
        Return a list of *argparse.add_argument* keyword-dicts.
        """

    @abstractmethod
    def validate_args(self, ns: argparse.Namespace) -> None:
        """
        Validate CLI args after parsing.  Raise *ValueError* on invalid combos.
        """

    @abstractmethod
    def examples(self) -> List[str]:
        """Return usage snippets for `--help` epilog."""

    @abstractmethod
    def get_system_description(self) -> str:
        """Optional extra context injected via a system-prompt."""

    # ------------------------------------------------------------------ #
    # Optional / overridable                                             #
    # ------------------------------------------------------------------ #
    def get_unique_id(self) -> str:
        """Return a unique identifier for the item. Override to use custom IDs."""
        return str(uuid.uuid4())

    def supported_output_formats(self) -> List[str]:
        """Override to narrow/widen acceptable output formats."""
        return ["json"]

    def post_process(self, raw: str) -> Any:  # noqa: ANN401 (Any is intentional)
        """
        Default implementation attempts JSON deserialisation; otherwise returns
        plain string.  Sub-classes can override for YAML/CSV, etc.
        """
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    # ------------------------------------------------------------------ #
    # Helper: factory                                                    #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_name(cls, name: str) -> "DataGeneratorTool":
        """Factory helper that returns a new instance of the requested tool.

        Parameters
        ----------
        name: str
            The unique `name` identifier declared on the desired tool class.

        Returns
        -------
        DataGeneratorTool
            A freshly-constructed instance of the matching tool.

        Raises
        ------
        KeyError
            If no tool with the supplied `name` has been registered.
        """
        try:
            tool_cls = cls._REGISTRY[name]
        except KeyError as exc:
            raise KeyError(f"No DataGeneratorTool registered with name '{name}'.") from exc
        return tool_cls()  # type: ignore[call-arg]
