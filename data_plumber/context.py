"""
# data_plumber/context.py

This module defines classes for referencing and handling of flow-logic
in a `Pipeline.run` (internal use).
"""

from typing import Any
from dataclasses import dataclass

from .output import _StageRecord


@dataclass
class PipelineContext:
    """
    Internal class providing a `Pipeline` execution-context for
    `stage.StageRef` classes.
    """

    records: list[_StageRecord]
    kwargs: dict[str, Any]
    out: Any
    count: int
