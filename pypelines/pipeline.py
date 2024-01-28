"""
# pypelines/pipeline.py

...
"""

from .output import PipelineOutput


class Pipeline:
    def run(self, **kwargs) -> PipelineOutput: ...
