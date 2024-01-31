"""
# data_plumber/stage.py

This module defines the `Stage`-class, a single data-processing unit of
a `Pipeline`.
"""

from typing import Optional, Callable, Any
from uuid import uuid4

from .context import StageRef


class Stage:
    """
    A `Stage` represents a single building block in the processing logic
    of a `Pipeline`. The set of arguments which are passed to a
    `Stage`'s `Callable` kwargs are given by (for actual arguments
    passed to `Callable`s refer to the lower section)
    * all kwargs given to `Pipeline.run` are forwarded (note that this
      makes the following parameters reserved words in this context),
    * `out` (an object that is passed through the entire `Pipeline`; its
      initial value is generated by the `Pipeline`'s `initialize_output`
      kwarg),
    * `primer` (output of `Stage.primer`),
    * `status` (output of `Stage.status`),
    * `count` (index of `Stage` in execution of `Pipeline`)

    Example usage:
     >>> from data_plumber import Stage
     >>> Stage(
             primer=lambda **kwargs: "data" in kwargs,
             status=lambda primer, **kwargs: int(primer),
             message=lambda primer, **kwargs:
                 "missing 'data'-argument" if not primer else ""
         )
     <data_plumber.stage.Stage object at ...>

    Keyword arguments:
    requires -- requirements for `Stage`-execution; dictionary with keys
                being either `None`, a `StageRef`, or `str` (identifier
                of a `Stage` in the context of a `Pipeline`; uses most
                recent evaluation) and values being either an integer
                (required output status of the keyed `Stage`) or a
                `Callable` taking the status as an argument and
                returning a `bool` (if it evaluates to `True`, the
                `Stage`-requirement is met); `PipelineError` is raised
                if references `Stage` has not yet been executed
    primer -- `Callable` for pre-processing data
              (kwargs: `out`, `count`)
              (default `lambda **kwargs: None`)
    action -- `Callable` for main-step of processing
              (kwargs: `out`, `primer`, `count`)
              (default `lambda **kwargs: None`)
    status -- `Callable` for generation of `Stage`'s integer exit status
              (kwargs: `out`, `primer`, `count`)
              (default `lambda **kwargs: 0`)
    message -- `Callable` for generation of `Stage`'s exit message
               (kwargs: `out`, `primer`, `count`, `status`)
               (default `lambda **kwargs: ""`)
    """

    def __init__(
        self,
        requires: Optional[
            dict[StageRef | str, int | Callable[[int], bool]]
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
        """Returns a `Stage`'s `id`."""
        return self._id

    @property
    def requires(self) -> Optional[
        dict[StageRef | str, int | Callable[[int], bool]]
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
    def message(self) -> Callable[..., str]:
        """Returns a `Stage`'s `message` callable."""
        return self._message

    def __add__(self, other):
        # import here to prevent circular import
        from .pipeline import Pipeline
        if not isinstance(other, Stage) and not isinstance(other, Pipeline):
            raise TypeError(
                "Incompatible type, expected 'Stage' or 'Pipeline' "
                    f"not '{type(other).__name__}'."
            )
        if isinstance(other, Stage):
            return Pipeline(self, other)
        other.prepend(self)
        return other

    def __str__(self):
        return self._id
