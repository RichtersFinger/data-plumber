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
from pypelines import Pipeline, Stage, Previous, First


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


# #############################
# ### Pipeline.exit_on_status

def test_pipeline_run_exit_on_status():
    """
    Test `Pipeline`-property `exit_on_status` with method `run` of
    class `Pipeline`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": 1}),
            status=lambda **kwargs: 1
        ),
        Stage(
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
        exit_on_status=1
    ).run()

    assert output.data == {"stage1": 1}


# #############################
# ### stage.requires

@pytest.mark.parametrize(
    ("status1", "status2", "out"),
    [
        (0, 0, {"stage1": 0, "stage2": 0, "stage3": 0}),
        (1, 0, {"stage1": 1, "stage3": 0}),
        (0, 1, {"stage1": 0, "stage2": 1}),
        (1, 1, {"stage1": 1}),
    ],
    ids=[
        "requirements_met",
        "requirements_not_met_1",
        "requirements_not_met_2",
        "requirements_not_met_12"
    ]
)
def test_pipeline_run_stage_requires_previous(status1, status2, out):
    """
    Test `requires`-property of `Stage` with `Previous`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": status1}),
            status=lambda **kwargs: status1
        ),
        Stage(
            requires={Previous: 0},
            action=lambda out, **kwargs: out.update({"stage2": status2}),
            status=lambda **kwargs: status2
        ),
        Stage(
            requires={Previous: 0},
            action=lambda out, **kwargs: out.update({"stage3": 0})
        ),
    ).run()

    assert output.data == out


@pytest.mark.parametrize(
    ("status", "out"),
    [
        (0, {"stage1": 0, "stage2": 0, "stage3": 0}),
        (1, {"stage1": 1}),
    ],
    ids=["requirements_met", "requirements_not_met"]
)
def test_pipeline_run_stage_requires_first(status, out):
    """
    Test `requires`-property of `Stage` with `First`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": status}),
            status=lambda **kwargs: status
        ),
        Stage(
            requires={First: 0},
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
        Stage(
            requires={First: 0},
            action=lambda out, **kwargs: out.update({"stage3": 0})
        ),
    ).run()

    assert output.data == out


@pytest.mark.parametrize(
    ("status", "out"),
    [
        (0, {"stage1": 0, "stage2": 0, "stage3": 0}),
        (1, {"stage1": 1, "stage2": 0}),
    ],
    ids=["requirements_met", "requirements_not_met"]
)
def test_pipeline_run_stage_requires_multiple(status, out):
    """
    Test `requires`-property of `Stage` with multiple requirements.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": status}),
            status=lambda **kwargs: status
        ),
        Stage(
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
        Stage(
            requires={First: 0, Previous: 0},
            action=lambda out, **kwargs: out.update({"stage3": 0})
        ),
    ).run()

    assert output.data == out


@pytest.mark.parametrize(
    ("status", "out"),
    [
        (0, {"stage1": 0, "stage2": 0}),
        (1, {"stage1": 1}),
    ],
    ids=["requirements_met", "requirements_not_met"]
)
def test_pipeline_run_stage_requires_callable(status, out):
    """
    Test `requires`-property of `Stage` with callable requirement.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": status}),
            status=lambda **kwargs: status
        ),
        Stage(
            requires={First: (lambda status: status != 1)},
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
    ).run()

    assert output.data == out
