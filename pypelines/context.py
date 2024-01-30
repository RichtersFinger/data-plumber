"""
# pypelines/context.py

...
"""

from typing import TypeAlias
from dataclasses import dataclass

StageOut: TypeAlias = tuple[str, str, int]


@dataclass
class PipelineContext:
    """
    Internal class providing a `Pipeline` execution-context for
    `stage.StageRef` classes.
    """

    stages: list[StageOut]
