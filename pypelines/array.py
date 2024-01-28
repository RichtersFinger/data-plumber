"""
# pypelines/array.py

...
"""

from .pipeline import Pipeline
from .output import PipelineOutput


class Pipearray:
    def __init__(
        self,
        *args: Pipeline,
        **kwargs: Pipeline
    ) -> None:
        ...

    def run(
        self,
        **kwargs
    ) -> list[PipelineOutput] | dict[str, PipelineOutput]:
        ...
