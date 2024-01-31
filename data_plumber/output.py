"""
# data_plumber/output.py

...
"""

from typing import Any
from dataclasses import dataclass

from .context import StageRecord


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
    def last_record(self) -> StageRecord:
        """Returns the last `Stage`'s result."""
        return self.records[-1]

    @property
    def last_status(self) -> int:
        """Returns the last `Stage`'s status result."""
        return self.records[-1][1]

    @property
    def last_message(self) -> str:
        """Returns the last `Stage`'s message result."""
        return self.records[-1][0]
