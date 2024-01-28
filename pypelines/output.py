"""
# pypelines/output.py

...
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class PipelineOutput:
    stages: list[tuple[str, int]]
    kwargs: dict[str, Any]
    data: Any
