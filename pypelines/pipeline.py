"""
# pypelines/pipeline.py

...
"""

from typing import Optional, Callable, Any, Iterator
from .stage import Stage
from .output import PipelineOutput


class Pipeline:
    def __init__(
        self,
        *args,
        initialize_output: Callable[..., Any] = lambda: {},
        exit_on_status: Optional[int] = None,
        loop: bool = False,
        **kwargs
    ) -> None: ...

    @property
    def id(self) -> str:
        ...

    def run(self, **kwargs) -> PipelineOutput:
        return PipelineOutput(None, None, None)

    def append(self, _) -> None:
        ...

    def prepend(self, _) -> None:
        ...

    def insert(self, index: int, _) -> None:
        ...

    def __iter__(self) -> Iterator[Stage]:
        ...
