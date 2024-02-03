"""
# data_plumber/ref.py

This module defines classes for referencing and handling of flow-logic
in a `Pipeline.run`.
"""

from typing import TypeAlias
import abc
from dataclasses import dataclass

from .context import PipelineContext
from .error import PipelineError


@dataclass
class StageRefOutput:
    """
    Record class identifying a `Stage` during `Pipeline.run`.

    Properties:
    stage -- string identifier of the referenced `Stage`
    index -- absolte position in execution order (stages)
    """
    stage: str
    index: int


class _StageRef(metaclass=abc.ABCMeta):
    """
    Base class enabling the definition of references to certain `Stage`s
    when executing a `Pipeline`. Only child-classes of this class are
    intended for explicit use.
    """

    STAGEREF_ERROR_MSG = \
        "Unable to resolve StageRef {target}{location} in Pipeline with " \
        + "stages {stages}. Records until error: {records}"

    @staticmethod
    def _format_records(records) -> str:
        return ' > '.join(map(str, records))

    @classmethod
    @abc.abstractmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        """
        Returns a `StageRefOutput` that given information on what is to
        be executed next. If this reference cannot be resolved within
        the given context, a `PipelineError` is raised.

        Keyword arguments:
        context -- `Pipeline` execution context
        """
        raise NotImplementedError("Missing definition of StageRef.get.")


StageRef: TypeAlias = type[_StageRef]
"""TypeAlias for type of _StageRef: type[_StageRef]"""


class Previous(_StageRef):
    """Reference to the previous `Stage` during `Pipeline` execution."""

    @classmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        if len(context.records) == 0:
            raise PipelineError(
                cls.STAGEREF_ERROR_MSG.format(
                    target="'Previous' ",
                    location=f"at index {str(context.current_position)}",
                    stages=str(context.stages),
                    records=cls._format_records(context.records)
                )
            )
        return StageRefOutput(
            context.records[-1].id_,
            context.records[-1].index
        )


class First(_StageRef):
    """Reference to the first `Stage` during `Pipeline` execution."""

    @classmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        if len(context.records) == 0:
            raise PipelineError(
                cls.STAGEREF_ERROR_MSG.format(
                    target="'First' ",
                    location=f"at index {str(context.current_position)}",
                    stages=str(context.stages),
                    records=cls._format_records(context.records)
                )
            )
        return StageRefOutput(
            context.records[0].id_,
            context.records[0].index
        )


class Last(_StageRef):
    """Reference to the last `Stage` of registered `Stage`s in `Pipeline`."""

    @classmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        if len(context.stages) == 0:
            raise PipelineError(
                cls.STAGEREF_ERROR_MSG.format(
                    target="'Last' ",
                    location="",
                    stages=str(context.stages),
                    records=cls._format_records(context.records)
                )
            )
        return StageRefOutput(
            context.stages[-1],
            len(context.stages) - 1
        )


class Next(_StageRef):
    """Reference to the next `Stage` of registered `Stage`s in `Pipeline`."""

    @classmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        stage_index = context.current_position + 1
        if context.loop:
            stage_index = stage_index % len(context.stages)
        try:
            return StageRefOutput(
                context.stages[stage_index],
                stage_index
            )
        except IndexError:  # allow Pipeline to exit via StageRef
            return StageRefOutput(
                "",
                stage_index
            )


class Skip(_StageRef):
    """Reference to the `Stage` after next of registered `Stage`s in `Pipeline`."""

    @classmethod
    def get(cls, context: PipelineContext) -> StageRefOutput:
        stage_index = context.current_position + 2
        if context.loop:
            stage_index = stage_index % len(context.stages)
        try:
            return StageRefOutput(
                context.stages[stage_index],
                stage_index
            )
        except IndexError:  # allow Pipeline to exit via StageRef
            return StageRefOutput(
                "",
                stage_index
            )


def StageById(stage_id: str) -> StageRef:
    """
    Reference to a `Stage` with its id. (First occurrence in
    `Pipeline`'s list of `Stage`s.)

    Keyword arguments:
    stage_id -- stage id
    """

    class _(_StageRef):
        @classmethod
        def get(cls, context: PipelineContext) -> StageRefOutput:
            try:
                index = context.stages.index(stage_id)
            except ValueError as exc:
                raise PipelineError(
                    cls.STAGEREF_ERROR_MSG.format(
                        target=f"to id '{stage_id}'",
                        location="",
                        stages=str(context.stages),
                        records=cls._format_records(context.records)
                    )
                ) from exc
            return StageRefOutput(
                stage_id,
                index
            )
    _.__doc__ = f"Reference to a `Stage` by the id '{stage_id}'. " \
        + "(First occurrence in `Pipeline`'s list of `Stage`s.)"

    return _


def StageByIndex(stage_index: int) -> StageRef:
    """
    Reference to the `Stage` with an absolute index.

    Keyword arguments:
    stage_index -- absolute index
    """

    class _(_StageRef):
        @classmethod
        def get(cls, context: PipelineContext) -> StageRefOutput:
            try:
                stage_id = context.stages[stage_index]
            except IndexError as exc:
                raise PipelineError(
                    cls.STAGEREF_ERROR_MSG.format(
                        target=f"to index '{str(stage_index)}'",
                        location="",
                        stages=str(context.stages),
                        records=cls._format_records(context.records)
                    )
                ) from exc
            return StageRefOutput(
                stage_id,
                stage_index
            )
    _.__doc__ = f"Reference to a `Stage` by its index of {str(stage_index)}."

    return _


def StageByIncrement(index_increment: int) -> StageRef:
    """
    Reference to the `Stage` with a given relative index.

    Keyword arguments:
    index_increment -- relative index
    """

    class _(_StageRef):
        @classmethod
        def get(cls, context: PipelineContext) -> StageRefOutput:
            stage_index = context.current_position + index_increment
            try:
                if context.loop:
                    stage_index = stage_index % len(context.stages)
                else:
                    if stage_index < 0:
                        raise IndexError(
                            f"Bad index '{stage_index}' in StageRef of non-looping Pipeline."
                        )
                stage_id = context.stages[stage_index]
            except IndexError as exc:
                raise PipelineError(
                    cls.STAGEREF_ERROR_MSG.format(
                        target=f"to index '{str(stage_index)}'",
                        location=f" (increment '{str(index_increment)}' from "
                            + f"'{str(context.current_position)}')",
                        stages=str(context.stages),
                        records=cls._format_records(context.records)
                    )
                ) from exc
            return StageRefOutput(
                stage_id,
                stage_index
            )
    _.__doc__ = f"Reference to a `Stage` by a relative index of {str(index_increment)}."

    return _
