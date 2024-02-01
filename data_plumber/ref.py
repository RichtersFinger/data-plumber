"""
# data_plumber/ref.py

This module defines classes for referencing and handling of flow-logic
in a `Pipeline.run`.
"""

from typing import Optional
import abc
from dataclasses import dataclass

from .context import PipelineContext
from .output import _StageRecord


def _get_next_stageref(context: PipelineContext, id_: str) \
        -> Optional[_StageRecord]:
    """Helper to get most recent `_StageRecord` of 'future'-`Stage`."""
    return next(
        (stage for _, stage in enumerate(reversed(context.records))
            if stage[0] == id_),
        None
    )


@dataclass
class StageRefOutput:
    """
    Record class identifying a `Stage` during `Pipeline.run`.

    Properties:
    stage -- string identifier of the references `Stage`
             (required)
    relative_index -- relative position in execution order
                      * if positive, follows context.stages
                      * if negative, follows context.records
                      (required)
    status -- most recent status value from the referenced `Stage`
              (optional; `None` implies 'not executed yet')
    """
    stage: str
    relative_index: int
    status: Optional[int] = None


class StageRef(metaclass=abc.ABCMeta):
    """
    Base class enabling the definition of references to certain `Stage`s
    when executing a `Pipeline`. Only child-classes of this class are
    intended for explicit use.
    """

    @staticmethod
    @abc.abstractmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        """
        Returns a `StageRefOutput` that given information on what is to
        be executed next. If this reference cannot be resolved within
        the given context, the value `None` is returned.

        Keyword arguments:
        context -- `Pipeline` execution context
        """
        raise NotImplementedError("Missing definition of StageRef.get.")


class Previous(StageRef):
    """Reference to the previous `Stage` during `Pipeline` execution."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        if len(context.records) == 0:
            return None
        return StageRefOutput(
            context.records[-1][0],
            -1,
            context.records[-1][2]
        )


class First(StageRef):
    """Reference to the first `Stage` during `Pipeline` execution."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        if len(context.records) == 0:
            return None
        return StageRefOutput(
            context.records[0][0],
            -context.current_position,
            context.records[0][2]
        )


class Last(StageRef):
    """Reference to the last `Stage` of registered `Stage`s in `Pipeline`."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        return StageRefOutput(
            context.stages[-1],
            len(context.stages) - 1 - context.current_position,
            x[2] if (x := _get_next_stageref(context, context.stages[-1]))
                else None
        )


class Next(StageRef):
    """Reference to the next `Stage` of registered `Stage`s in `Pipeline`."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        if context.current_position + 1 >= len(context.stages):
            return StageRefOutput("", 1, None)
        identifier = context.stages[context.current_position + 1]
        return StageRefOutput(
            identifier,
            1,
            x[2] if (x := _get_next_stageref(context, identifier))
                else None
        )


class Skip(StageRef):
    """Reference to the `Stage` after next of registered `Stage`s in `Pipeline`."""

    @staticmethod
    def get(context: PipelineContext) -> Optional[StageRefOutput]:
        if context.current_position + 2 >= len(context.stages):
            return StageRefOutput("", 2, None)
        identifier = context.stages[context.current_position + 2]
        return StageRefOutput(
            identifier,
            2,
            x[2] if (x := _get_next_stageref(context, identifier))
                else None
        )
