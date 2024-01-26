"""
Test suite for pypelines.

Run with
pytest -v -s --cov=pypelines.array \
    --cov=pypelines.error \
    --cov=pypelines.fitting \
    --cov=pypelines.pipeline \
    --cov=pypelines.response \
    --cov=pypelines.stage
"""

from pypelines import Pipeline, Stage


def test_pipeline_minimal():
    """Test method `trigger` of class `Pipeline` for minimal setup."""

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"test": 0})
        ),
    )
    output = pipeline.trigger()

    assert "test" in output.data
    assert output.data["test"] == 0
