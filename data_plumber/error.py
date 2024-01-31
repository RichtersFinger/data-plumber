"""
# data_plumber/error.py

This module defines data-plumber's custom exception types.
"""


class PipelineError(Exception):
    """Raised on error during `Pipeline.run`."""
    pass
