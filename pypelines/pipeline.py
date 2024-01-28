"""
# pypelines/pipeline.py

...
"""

from typing import Optional
from .output import PipelineOutput


class Pipeline:
    def __init__(
        self,
        *args,
        exit_on_status: Optional[int] = None,
        loop: bool = False,
        **kwargs
    ) -> None: ...

    def run(self, **kwargs) -> PipelineOutput:
        return PipelineOutput()
