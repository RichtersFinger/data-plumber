"""
# data_plumber/stage.py

This module defines the `Stage`-class, a single data-processing unit of
a `Pipeline`.
"""

from typing import Optional, Callable, Any

from .component import _PipelineComponent
from .ref import StageRef, StageById, StageByIncrement


class Stage(_PipelineComponent):
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

    `Callable`s are executed in the order:
    `primer` > `action` > `export` > `status` > `message`

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
    requires -- requirements for `Stage`-execution being either `None`
                or a dictionary with pairs of some reference to a `Stage`
                and the required status (uses most recent evaluation);

                key types are either `StageRef`, `str` (identifier of a
                `Stage` in the context of a `Pipeline`), or `int`
                (relative index in `Pipeline` stage arrangement);

                values are either an integer value or a `Callable`
                taking the status as an argument and returning a `bool`
                (if it evaluates to `True`, the `Stage`-requirement is
                met); `PipelineError` is raised if referenced `Stage`
                has not yet been executed
    primer -- `Callable` for pre-processing data
              (kwargs: `out`, `count`)
              (default `lambda **kwargs: None`)
    action -- `Callable` for main-step of processing
              (kwargs: `out`, `primer`, `count`)
              (default `lambda **kwargs: None`)
    export -- `Callable` that returns a dictionary of additional kwargs
              to be exported to the parent `Pipeline`; in the following
              `Stage`s, these kwargs are then available as if they were
              provided with the `Pipeline.run`-command
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
            dict[StageRef | str | int, int | Callable[[int], bool]]
        ] = None,
        primer: Callable[..., Any] = lambda **kwargs: None,
        action: Callable[..., Any] = lambda **kwargs: None,
        export: Optional[Callable[..., Optional[dict[str, Any]]]] = None,
        status: Callable[..., int] = lambda **kwargs: 0,
        message: Callable[..., str] = lambda **kwargs: ""
    ) -> None:
        if requires is None:
            self._requires = None
        else:
            self._requires = {}
            for k, v in requires.items():
                if isinstance(k, str):
                    self._requires[StageById(k)] = v
                elif isinstance(k, int):
                    self._requires[StageByIncrement(k)] = v
                else:
                    self._requires[k] = v
        self._primer = primer
        self._action = action
        if export is None:
            self._export: Callable[..., dict[str, Any]] = lambda **kwargs: {}
        else:
            self._export = export  # type: ignore[assignment]
        self._status = status
        self._message = message
        super().__init__()

    @property
    def requires(self) -> Optional[
        dict[StageRef, int | Callable[[int], bool]]
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
    def export(self) -> Callable[..., Any]:
        """Returns a `Stage`'s `export` callable."""
        return self._export

    @property
    def status(self) -> Callable[..., int]:
        """Returns a `Stage`'s `status` callable."""
        return self._status

    @property
    def message(self) -> Callable[..., str]:
        """Returns a `Stage`'s `message` callable."""
        return self._message
