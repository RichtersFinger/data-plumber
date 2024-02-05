"""
# data_plumber/output.py

This module defines the output-format `PipelineOutput` of a
`Pipeline.run`.
"""

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class StageRecord:
    """
    Record of a `Stage`'s execution result.

    Keyword arguments:
    index -- position in `Pipeline`'s list of `Stage`s
    id_ -- `Stage` identifier (in `Pipeline`)
    message -- string returned by `Stage`'s `message`-`Callable`
    status -- int returned by `Stage`'s `status`-`Callable`
    """
    index: int
    id_: str
    message: str
    status: int

    # keep legacy support (where a StageRecord was an alias for a two-tuple)
    def __getitem__(self, index):
        if index == 0:
            return self.message
        if index == 1:
            return self.status
        if index == 2:
            return self.index
        if index == 3:
            return self.id_
        raise IndexError(f"Bad index '{index}' in StageRecord.")

    def __eq__(self, other):
        if isinstance(other, tuple) and len(other) == 2:
            return (self.message, self.status) == other
        if isinstance(other, StageRecord):
            return \
                self.index == other.index \
                and self.id_ == other.id_ \
                and self.message == other.message \
                and self.status == other.status
        return False

    def __iter__(self):
        for s in (self.message, self.status):
            yield s


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
