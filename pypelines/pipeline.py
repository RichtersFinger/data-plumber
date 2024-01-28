"""
# pypelines/pipeline.py

...
"""

from typing import Optional, Callable, Any
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

    def run(self, **kwargs) -> PipelineOutput:
        return PipelineOutput(None, None, None)
