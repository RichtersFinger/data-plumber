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

import pytest
from pypelines import Pipeline, Stage


# #############################
# ### Pipeline.run

def test_pipeline_minimal():
    """Test method `run` of class `Pipeline` for minimal setup."""

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"test": 0})
        ),
    ).run()

    assert "test" in output.data
    assert output.data["test"] == 0


def test_pipeline_run_minimal_two_stage():
    """
    Test method `run` of class `Pipeline` for minimal two-stage setup.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": 0})
        ),
        Stage(
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
    ).run()

    assert "stage1" in output.data
    assert output.data["stage1"] == 0
    assert "stage2" in output.data
    assert output.data["stage2"] == 0


def test_pipeline_run_exit_on_status():
    """
    Test `Pipeline`-property `exit_on_status` with method `run` of
    class `Pipeline`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": 0}),
            status=lambda **kwargs: 1
        ),
        Stage(
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
        exit_on_status=1
    ).run()

    assert "stage1" in output.data
    assert output.data["stage1"] == 0
    assert "stage2" not in output.data


@pytest.mark.parametrize(
    ("status", "out"),
    [
        (0, {"stage1": 0, "stage2": 0}),
        (1, {"stage1": 0}),
    ],
    ids=["requirements_met", "requirements_not_met"]
)
def test_pipeline_run_stage_requires_previous(status, out):
    """
    Test `requires`-property of `Stage`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": 0}),
            status=lambda **kwargs: status
        ),
        Stage(
            requires={Previous: 0},
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
    ).run()

    assert output.data == out
