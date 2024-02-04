"""
# data_plumber/component.py

This module defines the `_PipelineComponent`-class, a base class for
`Pipeline`-components like `Stage`.
"""

from uuid import uuid4


class _PipelineComponent:
    """
    Base class for components of a `Pipeline`.
    """
    def __init__(self) -> None:
        self._id = str(uuid4())

    @property
    def id(self) -> str:
        """Returns a `Stage`'s `id`."""
        return self._id

    def __add__(self, other):
        # import here to prevent circular import
        from .pipeline import Pipeline
        if not isinstance(other, _PipelineComponent) \
                and not isinstance(other, Pipeline):
            raise TypeError(
                "Incompatible type, expected '_PipelineComponent' or 'Pipeline'"
                    + f" not '{type(other).__name__}'."
            )
        if isinstance(other, _PipelineComponent):
            return Pipeline(self, other)
        other.prepend(self)
        return other

    def __str__(self):
        return self._id
