"""
# pypelines/fork.py

...
"""

from typing import Callable, Optional
from uuid import uuid4
from .context import PipelineContext, StageRef


class Fork:
    """
    A `Fork` can be inserted into a `Pipeline` to control flow/execution
    order of a `Pipeline.run(...)`-command. This class is not indended
    for direct use, but taylored to be integrated into a `Pipeline`. It
    is initialized with a callable that returns either a `StageRef` or
    `str`-identifier of a `Stage`. Supported input arguments are (in the
    context of `Pipeline` execution, `Stage` for more details)
    * `in_` (dictionary with kwargs of `Pipeline.run`),
    * `out` (an object that is passed through the entire `Pipeline`),
    * `count` (index of `Stage` in execution of `Pipeline`)

    A return value of `None` for the callable is treated as a request to
    exit the `Pipeline` execution.

    Keyword arguments:
    fork -- callable that returns a reference to a `Stage`
            (kwargs: `in_`, `out`, `count`)
    """

    def __init__(
        self,
        fork: Callable[..., Optional[StageRef | str]]
    ) -> None:
        self._fork = fork
        self._id = str(uuid4())

    @property
    def id(self) -> str:
        """Returns a `Stage`'s `id`."""
        return self._id

    def eval(self, context: PipelineContext) -> Optional[StageRef | str]:
        """
        Returns the value from evaluation of the `Fork`s conditional
        function.

        Keyword arguments:
        context -- `Pipeline` execution context
        """

        return self._fork(
            in_=context.kwargs, out=context.out, count=context.count
        )
