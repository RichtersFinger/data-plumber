"""
# pypelines/fork.py

...
"""

from typing import Callable, Optional
from .stage import StageRef


class Fork:
    def __init__(
        self,
        _: Callable[..., Optional["StageRef | str"]]
    ) -> None: ...

    def eval(self, **kwargs) -> Optional[str]: ...
