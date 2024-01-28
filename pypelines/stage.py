"""
# pypelines/stage.py

This module defines the `Stage` as well as `StageRef` classes. While the
former constitute the individual logical units of a `Pipeline` the
latter serve as references to specific `Stages` during the execution of
a `Pipeline` (see examples for `Stage.requires`). Note that the
requirement evaluation logic only has meaning in the context of a
`Pipeline`.

Example usage
  >>> from pypelines import Stage, Previous
  >>> Stage(requires={Previous: 0}, status=lambda in_, **kwargs: int("data" in in_))
  <pypelines.stage.Stage object at ...>
"""

from typing import Optional, Callable, Any
import abc
from uuid import uuid4
from .context import PipelineContext


class Stage:
    """
    A `Stage` represents a single building block in the processing logic
    of a `Pipeline`. The arguments of which one or more are passed to a
    `Stage`'s `Callable` kwargs are given by
    * `in_` (dictionary with kwargs of `Pipeline.run`),
    * `out` (an object that is passed through the entire `Pipeline`),
    * `primer` (output of `Stage.primer`),
    * `status` (output of `Stage.status`),
    * `count` (index of `Stage` in execution of `Pipeline`)

    Keyword arguments:
    requires -- requirements for `Stage`-execution; dictionary with keys
                being either `None`, a `StageRef`, or `str` (identifier
                of a `Stage` in the context of a `Pipeline`) and values
                being either an integer (required output status of the
                keyed `Stage`) or a `Callable` taking the status as an
                argument and returning a `bool` (if it evaluates to
                `True`, the `Stage`-requirement is met)
    primer -- `Callable` for pre-processing data
              (kwargs: `in_`, `out`, `count`)
              (default `lambda **kwargs: None`)
    action -- `Callable` for main-step of processing
              (kwargs: `in_`, `out`, `primer`, `count`)
              (default `lambda **kwargs: None`)
    status -- `Callable` for generation of `Stage`'s integer exit status
              (kwargs: `in_`, `out`, `primer`, `count`)
              (default `lambda **kwargs: 0`)
    message -- `Callable` for generation of `Stage`'s exit message
               (kwargs: `in_`, `out`, `primer`, `count`, `status`)
               (default `lambda **kwargs: ""`)
    """

    def __init__(
        self,
        requires: Optional[
            dict["Optional[StageRef | str]", "int | Callable[[int], bool]"]
        ] = None,
        primer: Callable[..., Any] = lambda **kwargs: None,
        action: Callable[..., Any] = lambda **kwargs: None,
        status: Callable[..., int] = lambda **kwargs: 0,
        message: Callable[..., str] = lambda **kwargs: ""
    ) -> None:
        self._requires = requires
        self._primer = primer
        self._action = action
        self._status = status
        self._message = message
        self._id = str(uuid4())

    @property
    def id(self) -> str:
        """Returns a `Stage`'s id."""
        return self._id

    @property
    def requires(self) -> Optional[
        dict["Optional[StageRef | str]", "int | Callable[[int], bool]"]
    ]:
        """Returns a `Stage`'s requirements."""
        return self._requires

    @property
    def primer(self) -> Callable[..., Any]:
        """Returns a `Stage`'s `primer` callable."""
        return self._primer

    @property
    def action(self) -> Callable[..., Any]:
        """Returns a `Stage`'s `action` callable."""
        return self._action

    @property
    def status(self) -> Callable[..., int]:
        """Returns a `Stage`'s `status` callable."""
        return self._status

    @property
    def message(self) -> Callable[..., int]:
        """Returns a `Stage`'s `message` callable."""
        return self._message


class StageRef(metaclass=abc.ABCMeta):
    """
    Base class enabling the definition of references to certain `Stage`s
    when executing a `Pipeline`. Only child-classes of this class are
    intended for explicit use.
    """

    @staticmethod
    @abc.abstractmethod
    def get(context: PipelineContext):
        """Returns the `Stage` that is to be executed next."""
        raise NotImplementedError("Missing definition of StageRef.get.")


class Previous(StageRef):
    """Reference to the previous `Stage` during `Pipeline` execution."""


class First(StageRef):
    """Reference to the first `Stage` during `Pipeline` execution."""
