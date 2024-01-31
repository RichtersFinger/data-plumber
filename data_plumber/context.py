"""
# data_plumber/context.py

This module defines classes for referencing and handling of flow-logic
in a `Pipeline.run` (internal use).
"""

from typing import TypeAlias, Any, Optional
import abc
from dataclasses import dataclass

_StageRecord: TypeAlias = tuple[str, str, int]
"""Tuple of `Stage`-identifier and evaluated message and status."""
StageRecord: TypeAlias = tuple[str, int]
"""Tuple of message and status from a `Stage`'s-evaluation."""


@dataclass
class PipelineContext:
    """
    Internal class providing a `Pipeline` execution-context for
    `stage.StageRef` classes.
    """

    stages: list[_StageRecord]
    kwargs: dict[str, Any]
    out: Any
    count: int


class StageRef(metaclass=abc.ABCMeta):
    """
    Base class enabling the definition of references to certain `Stage`s
    when executing a `Pipeline`. Only child-classes of this class are
    intended for explicit use.
    """

    @staticmethod
    @abc.abstractmethod
    def get(context: PipelineContext) -> Optional[_StageRecord]:
        """
        Returns the `Stage` that is to be executed next. If this
        reference cannot be resolved within the given context, the value
        `None` is returned.

        Keyword arguments:
        context -- `Pipeline` execution context
        """
        raise NotImplementedError("Missing definition of StageRef.get.")


class Previous(StageRef):
    """Reference to the previous `Stage` during `Pipeline` execution."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[_StageRecord]:
        try:
            return context.stages[-1]
        except IndexError:
            return None


class First(StageRef):
    """Reference to the first `Stage` during `Pipeline` execution."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[_StageRecord]:
        try:
            return context.stages[0]
        except IndexError:
            return None
