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

    Properties:
    stages -- list of string identifiers of `Pipeline`-components in
              order of their registration (= order of execution with
              `Fork`s)
    current_position -- index of current position in stages
    loop -- `loop`-property of `Pipeline`
    records -- list of previous `_StageRecord`s for the current
               `Pipeline.run`
    kwargs -- kwargs passed to `Pipeline.run`
    out -- persistent data-object passed through a `Pipeline`
    count -- index of previously executed `Stage`s
    """

    stages: list[str]
    current_position: int
    loop: bool
    records: list[_StageRecord]
    kwargs: dict[str, Any]
    out: Any
    count: int
