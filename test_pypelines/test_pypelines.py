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
# ### PipelineOutput

def test_pipeline_output_minimal():
    """Test properties of class `PipelineOutput` for minimal setup."""

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"test": 0}),
            status=lambda **kwargs: 0,
            message=lambda **kwargs: "stage 1"
        ),
    ).run(input="input")

    assert hasattr(output, "stages")
    assert hasattr(output, "kwargs")
    assert hasattr(output, "data")

    assert isinstance(output.stages, list)
    assert len(output.stages) == 1
    assert output.stages[0] == ("stage 1", 0)
    assert isinstance(output.data, dict)
    assert output.data == {"test": 0}
    assert isinstance(output.kwargs, dict)
    assert output.kwargs == {"input": "input"}


def test_pipeline_output_two_stage():
    """Test properties of class `PipelineOutput` for two-`Stage` setup."""

    output = Pipeline(
        Stage(
            status=lambda **kwargs: 0,
            message=lambda **kwargs: "stage 1"
        ),
        Stage(
            status=lambda **kwargs: 1,
            message=lambda **kwargs: "stage 2"
        ),
    ).run()

    assert len(output.stages) == 2
    assert output.stages[0] == ("stage 1", 0)
    assert output.stages[1] == ("stage 2", 1)


# #############################
# ### Pipeline.initialize_output

def test_pipeline_run_initialize_output():
    """
    Test `Pipeline`-property `initialize_output` with method `run`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(0),
            status=lambda **kwargs: 0
        ),
        initialize_output=lambda: []
    ).run()

    assert isinstance(output.data, list)
    assert len(output.data) == 1
    assert output.data[0] == 0


# #############################
# ### Pipeline.exit_on_status

def test_pipeline_run_exit_on_status():
    """
    Test `Pipeline`-property `exit_on_status` with method `run`.
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
# ### Stage.primer

def test_stage_primer_minimal():
    """Test property `primer` of class `Stage` for minimal setup."""

    output = Pipeline(
        Stage(
            primer=lambda **kwargs: "primer",
            action=lambda out, primer, **kwargs: out.update({"test": primer})
        ),
    ).run()

    assert "test" in output.data
    assert output.data["test"] == "primer"


# #############################
# ### Stage.requires

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


# #############################
# ### Pipeline.named stages

def test_pipeline_named_stages_minimal():
    """
    Test method `run` of class `Pipeline` for minimal setup of named
    `Stage`s.
    """

    output = Pipeline(
        "a",
        a=Stage(
            action=lambda out, **kwargs: out.update({"test": 0})
        ),
    ).run()

    assert "test" in output.data
    assert output.data["test"] == 0


def test_pipeline_named_stages_execution_order():
    """
    Test execution order for method `run` of class `Pipeline` for named
    `Stage`s.
    """

    output = Pipeline(
        "a", "b", "a",
        a=Stage(
            action=lambda out, **kwargs: out.append["a"]
        ),
        b=Stage(
            action=lambda out, **kwargs: out.append["b"]
        ),
        initialize_output=lambda: [],
    ).run()

    assert output.data == ["a", "b", "a"]


# #############################
# ### Pipeline.named stages

def test_pipeline_loop_minimal():
    """
    Test property `loop` with method `run` of class `Pipeline` for
    minimal setup.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"test": out["test"] + 1}),
            status=lambda out, **kwargs: 0 if out["test"] < 3 else 1,
        ),
        initialize_output=lambda: {"test": 0},
        exit_on_status=1,
        loop=True,
    ).run()

    assert "test" in output.data
    assert output.data["test"] == 3
    assert len(output.stages) == 3
