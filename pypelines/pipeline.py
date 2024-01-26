"""
# pypelines/pipeline.py

...
"""

from .output import PipelineOutput


class Pipeline:
    def trigger(self, **kwargs) -> PipelineOutput: ...
