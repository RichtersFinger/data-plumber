"""
# data_plumber/output.py

This module defines the output-format `PipelineOutput` of a
`Pipeline.run`.
"""

from typing import TypeAlias, Any, Optional
from dataclasses import dataclass


_StageRecord: TypeAlias = tuple[str, str, int]
"""Tuple of `Stage`-identifier and evaluated message and status."""
StageRecord: TypeAlias = tuple[str, int]
"""Tuple of message and status from a `Stage`'s-evaluation."""


@dataclass
class PipelineOutput:
    """
    Response type of a call to `Pipeline.run`.

    Its properties are:
    * `records`: list of `StageRecord`s (tuples) containing all messages
                 and status values for the executed `Stage`s in a
                 `Pipeline.run`
    * `kwargs`: kwargs passed to `Pipeline.run`
    * `data`: reference to the persistent object that has been passed
              through the `Pipeline`

    Additional convenience methods:
    * `last_record`: returns `StageRecord` of last `Stage` before
                     `Pipeline` exited
    * `last_status`: returns `status` of last `Stage` before `Pipeline`
                     exited
    * `last_message`: returns `message` of last `Stage` before
                      `Pipeline` exited
    """

    records: list[StageRecord]
    kwargs: dict[str, Any]
    data: Any

    @property
    def last_record(self) -> Optional[StageRecord]:
        """Returns the last `Stage`'s result."""
        try:
            return self.records[-1]
        except IndexError:
            return None

    @property
    def last_status(self) -> Optional[int]:
        """Returns the last `Stage`'s status result."""
        try:
            return self.records[-1][1]
        except IndexError:
            return None

    @property
    def last_message(self) -> Optional[str]:
        """Returns the last `Stage`'s message result."""
        try:
            return self.records[-1][0]
        except IndexError:
            return None
