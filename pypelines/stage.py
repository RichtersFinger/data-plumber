"""
# pypelines/stage.py

...
"""

from typing import Optional, Callable, Any


class StageRef:
    pass
class Previous(StageRef):
    pass
class First(StageRef):
    pass


class Stage:
    def __init__(
        self,
        requires: Optional[
            dict["StageRef | str", "int | Callable[[int], bool]"]
        ] = None,
        primer: Optional[Callable[..., Any]] = None,
        action: Optional[Callable[..., Any]] = None,
        status: Optional[Callable[..., int]] = None,
        message: Optional[Callable[..., str]] = None
    ) -> None:
        pass
