"""
# data_plumber/ref.py

This module defines classes for referencing and handling of flow-logic
in a `Pipeline.run`.
"""

from typing import Optional
import abc

from .output import _StageRecord
from .context import PipelineContext


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
            return context.records[-1]
        except IndexError:
            return None


class First(StageRef):
    """Reference to the first `Stage` during `Pipeline` execution."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[_StageRecord]:
        try:
            return context.records[0]
        except IndexError:
            return None
