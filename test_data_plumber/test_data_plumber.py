"""
Test suite for data-plumber.

Run with
pytest -v -s --cov=data_plumber.array \
    --cov=data_plumber.component \
    --cov=data_plumber.context \
    --cov=data_plumber.error \
    --cov=data_plumber.fork \
    --cov=data_plumber.output \
    --cov=data_plumber.pipeline \
    --cov=data_plumber.ref \
    --cov=data_plumber.stage
"""

import pytest
from data_plumber \
    import Pipeline, Stage, Previous, First, Last, Next, Skip, Fork, \
        PreviousN, NextN, StageById, StageByIndex, StageByIncrement, \
        PipelineError, Pipearray
from data_plumber.context import PipelineContext
from data_plumber.output import PipelineOutput


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


def test_pipeline_minimal_pass_through():
    """
    Test method `run` of class `Pipeline` for pass through of kwargs in
    minimal setup.
    """

    test_arg0 = 0

    output = Pipeline(
        Stage(
            action=lambda out, test_arg, **kwargs:
                out.update({"test": test_arg})
        ),
        Stage(
            action=lambda out, **kwargs:
                out.update({"test2": kwargs["test_arg"]})
        ),
    ).run(test_arg=test_arg0)

    assert "test" in output.data
    assert output.data["test"] == test_arg0
    assert output.data["test2"] == test_arg0


def test_pipeline_minimal_export():
    """
    Test method `run` of class `Pipeline` for exporting additional
    kwargs from `Stage`.
    """

    test_arg0 = 1

    output = Pipeline(
        Stage(  # export kwarg
            export=lambda **kwargs: {"new_kw": test_arg0}
        ),
        Stage(  # write that kwarg into output.data
            action=lambda out, new_kw, **kwargs:
                out.update({"new_kw": new_kw})
        ),
    ).run()

    assert "new_kw" in output.data
    assert output.data["new_kw"] == test_arg0


@pytest.mark.parametrize(
    "kwarg",
    ["out", "primer", "status", "count"]
)
def test_pipeline_reserved_kwargs(kwarg):
    """
    Test exception behavior of method `run` of class `Pipeline` for
    reserved keywords.
    """

    with pytest.raises(PipelineError):
        Pipeline(
            Stage(),
        ).run(**{kwarg: 0})


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

    assert hasattr(output, "records")
    assert hasattr(output, "kwargs")
    assert hasattr(output, "data")
    assert hasattr(output, "last_record")
    assert hasattr(output, "last_message")
    assert hasattr(output, "last_status")

    assert isinstance(output.records, list)
    assert len(output.records) == 1
    assert output.records[0] == ("stage 1", 0)
    assert output.last_record == ("stage 1", 0)
    assert (output.last_message, output.last_status) == ("stage 1", 0)
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

    assert len(output.records) == 2
    assert output.records[0] == ("stage 1", 0)
    assert output.records[1] == ("stage 2", 1)


def test_pipeline_output_empty():
    """
    Test properties of class `PipelineOutput.last_X` in case of empty
    output.
    """

    output = Pipeline().run()

    assert output.last_message is None
    assert output.last_status is None
    assert output.last_record is None

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
# ### Pipeline.run_for_kwargs

def test_pipeline_run_for_kwargs():
    """
    Test method `run_for_kwargs` of `Pipeline`.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, outer_arg, **kwargs:
                out.update({"arg": outer_arg})
        ),
    )

    @pipeline.run_for_kwargs(outer_arg=0)
    def f(arg):
        return arg

    assert f() == 0


def test_pipeline_run_for_kwargs_multiple():
    """
    Test method `run_for_kwargs` of `Pipeline` (only partial generation
    of kwargs from pipeline).
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, outer_arg, **kwargs:
                out.update({"arg1": outer_arg})
        ),
    )

    @pipeline.run_for_kwargs(outer_arg=0)
    def f(arg1, arg2):
        return (arg1, arg2)

    assert f(arg2=1) == (0, 1)


def test_pipeline_run_for_kwargs_multiple_priority():
    """
    Test method `run_for_kwargs` of `Pipeline` (priority of kwargs).
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, outer_arg, **kwargs:
                out.update({"arg1": outer_arg})
        ),
    )

    @pipeline.run_for_kwargs(outer_arg=0)
    def f(arg1, arg2):
        return (arg1, arg2)

    assert f(arg1=2, arg2=1) == (2, 1)


# #############################
# ### Pipeline.finalize_output

def test_pipeline_run_finalize_output():
    """
    Test `Pipeline`-property `finalize_output` with method `run`.
    """

    output = Pipeline(
        Stage(),
        finalize_output=lambda data, **kwargs: data.update(kwargs)
    ).run(finalizer="finalizer")

    assert "finalizer" in output.data
    assert output.data["finalizer"] == "finalizer"


def test_pipeline_run_finalize_output_override():
    """
    Test `Pipeline`-property `finalize_output` with method `run`.
    """

    output = Pipeline(
        Stage(),
        finalize_output=lambda data, **kwargs: data.update(kwargs)
    ).run(
        finalizer="finalizer",
        finalize_output=lambda data, **kwargs:
            data.update({"finalizer-override": True})
    )

    assert "finalizer" not in output.data
    assert "finalizer-override" in output.data
    assert output.data["finalizer-override"]


@pytest.mark.parametrize(
    ("status", "expected_out"),
    [
        (0, {"status": 0}),
        (1, {}),
    ]
)
def test_pipeline_run_finalize_output_records(status, expected_out):
    """
    Test `Pipeline`-property `finalize_output` using `records`-
    information.
    """

    output = Pipeline(
        Stage(status=lambda **kwargs: status),
        finalize_output=lambda data, records, **kwargs:
            data.update({"status": 0}) if records[-1].status == 0 else None
    ).run()

    assert output.data == expected_out


@pytest.mark.parametrize(
    ("status", "expected_out"),
    [
        (0, {"status": 0}),
        (1, {}),
    ]
)
def test_pipeline_run_finalize_output_records_run(status, expected_out):
    """
    Test `Pipeline`-property `finalize_output` using `records`-
    information (repeat previous test `..._finalize_output_records `but
    for run-specific `finalize_output`).
    """

    output = Pipeline(
        Stage(status=lambda **kwargs: status),
    ).run(
        finalize_output=lambda data, records, **kwargs:
            data.update({"status": 0}) if records[-1].status == 0 else None
    )

    assert output.data == expected_out


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


def test_pipeline_run_exit_on_status_callable():
    """
    Test `Pipeline`-property `exit_on_status` as callable with method
    `run`.
    """

    output = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.update({"stage1": 1}),
            status=lambda **kwargs: 1
        ),
        Stage(
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
        exit_on_status=lambda status: status > 0
    ).run()

    assert output.data == {"stage1": 1}


# #############################
# ### Pipeline.len

def test_pipeline_len():
    """
    Test `Pipeline`-property `exit_on_status` with method `run`.
    """

    pipeline = Pipeline(
        Stage(),
    )

    assert len(pipeline) == 1

    pipeline = Pipeline(
        Stage(),
        Stage(),
    )

    assert len(pipeline) == 2


# #############################
# ### Pipeline extension with Stages

def _pipeline_extension_input():
    return [
        Stage(
            action=lambda out, **kwargs: out.append(1)
        ),
        Pipeline(
            Stage(
                action=lambda out, **kwargs: out.append(1)
            ),
        ),
    ]


@pytest.mark.parametrize(
    ("stage_or_pipeline"),
    _pipeline_extension_input(),
    ids=["Stage", "Pipeline"]
)
def test_pipeline_append(stage_or_pipeline):
    """
    Test method `append` of `Pipeline` with `Stage` or `Pipeline`.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
        initialize_output=lambda: []
    )

    assert len(pipeline) == 1

    pipeline.append(
        stage_or_pipeline
    )

    assert len(pipeline) == 2

    output = pipeline.run()

    assert output.data == [0, 1]


@pytest.mark.parametrize(
    ("stage_or_pipeline"),
    _pipeline_extension_input(),
    ids=["Stage", "Pipeline"]
)
def test_pipeline_prepend(stage_or_pipeline):
    """
    Test method `prepend` of `Pipeline` with `Stage` or `Pipeline`.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
        initialize_output=lambda: []
    )

    assert len(pipeline) == 1

    pipeline.prepend(
        stage_or_pipeline
    )

    assert len(pipeline) == 2

    output = pipeline.run()

    assert output.data == [1, 0]


@pytest.mark.parametrize(
    ("stage_or_pipeline"),
    _pipeline_extension_input(),
    ids=["Stage", "Pipeline"]
)
def test_pipeline_insert(stage_or_pipeline):
    """
    Test method `insert` of `Pipeline` with `Stage` or `Pipeline`.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
        initialize_output=lambda: []
    )

    assert len(pipeline) == 1

    pipeline.insert(
        0,
        stage_or_pipeline
    )
    pipeline.insert(
        2,
        stage_or_pipeline
    )

    assert len(pipeline) == 3

    output = pipeline.run()

    assert output.data == [1, 0, 1]


def test_pipeline_append_named():
    """
    Test extension method `append` of `Pipeline` with named `Stage`s.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(1)
        ),
        initialize_output=lambda: []
    )

    pipeline.append(
        "a",
        a=Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
    )

    assert pipeline.run().data == [1, 0]


def test_pipeline_prepend_named():
    """
    Test extension method `prepend` of `Pipeline` with named `Stage`s.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(1)
        ),
        initialize_output=lambda: []
    )

    pipeline.prepend(
        "a",
        a=Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
    )

    assert pipeline.run().data == [0, 1]


def test_pipeline_insert_named():
    """
    Test extension method `insert` of `Pipeline` with named `Stage`s.
    """

    pipeline = Pipeline(
        Stage(
            action=lambda out, **kwargs: out.append(1)
        ),
        initialize_output=lambda: []
    )

    pipeline.insert(
        0,
        "a",
        a=Stage(
            action=lambda out, **kwargs: out.append(0)
        ),
    )

    assert pipeline.run().data == [0, 1]


# #############################
# ### Pipeline unpacking

def test_pipeline_unpacking():
    """Test method `__iter__` for class `Pipeline`."""

    stage_a = Stage()
    stage_b = Stage()

    pipeline = Pipeline(stage_a, stage_b)

    pipeline2 = Pipeline(*pipeline)

    assert len(pipeline2) == 2

    x, y = pipeline

    assert x == stage_a
    assert y == stage_b


def test_pipeline_unpacking_mapping():
    """Test method `__iter__` for class `Pipeline`."""

    stage_a = Stage(
        action=lambda out, **kwargs: out.append("stage_a")
    )
    stage_b = Stage(
        action=lambda out, **kwargs: out.append("stage_b")
    )

    pipeline = Pipeline("a", "b", a=stage_a, b=stage_b)

    output = Pipeline(
        "b", "a",
        **pipeline,
        initialize_output=lambda: []
    ).run()

    assert output.data == ["stage_b", "stage_a"]


# #############################
# ### empty PipelineComponent

def test_pipeline_empty_component():
    """
    Test empty `PipelineComponent` behavior in `Pipeline.run`.
    """

    output = Pipeline(
        Stage(),
        "empty_component"
    ).run()

    assert len(output.records) == 1


def test_pipeline_fork_empty_component():
    """
    Test returning string-id of empty `PipelineComponent` from `Fork`-
    conditional in `Pipeline.run`.
    """

    output = Pipeline(
        Fork(
            lambda **kwargs: "fork_target"
        ),
        Stage(),
        "fork_target",
        Stage()
    ).run()

    assert len(output.records) == 1


# #############################
# ### Pipeline/Stage.addition

def test_stage_addition():
    """Test method `__add__` for class `Stage`."""

    stage_a = Stage(
        action=lambda out, **kwargs: out.update({"stage_a": 0})
    )
    stage_b = Stage(
        action=lambda out, **kwargs: out.update({"stage_b": 0})
    )
    pipeline = stage_a + stage_b

    assert isinstance(pipeline, Pipeline)

    output = pipeline.run()

    assert output.data == {"stage_a": 0, "stage_b": 0}


def test_stage_pipeline_addition_multiple():
    """Test method `__add__` for classes `Pipeline` and `Stage`."""

    stage_a = Stage(
        action=lambda out, **kwargs: out.update({"stage_a": 0})
    )
    stage_b = Stage(
        action=lambda out, **kwargs: out.update({"stage_b": 0})
    )
    stage_c = Stage(
        action=lambda out, **kwargs: out.update({"stage_c": 0})
    )
    pipeline_a = (stage_a + stage_b) + stage_c
    pipeline_b = stage_a + (stage_b + stage_c)
    pipeline_c = (stage_a + stage_a) + (stage_b + stage_b)

    assert isinstance(pipeline_a, Pipeline)
    assert isinstance(pipeline_b, Pipeline)
    assert isinstance(pipeline_c, Pipeline)

    output_a = pipeline_a.run()
    output_b = pipeline_b.run()
    output_c = pipeline_c.run()

    assert output_a.data == {"stage_a": 0, "stage_b": 0, "stage_c": 0}
    assert output_b.data == {"stage_a": 0, "stage_b": 0, "stage_c": 0}
    assert output_c.data == {"stage_a": 0, "stage_b": 0}
    assert len(output_c.records) == 4


def test_stage_addition_exception():
    """
    Test method `__add__` for classes `Stage`/`Pipeline` with bad types.
    """

    # Stage
    with pytest.raises(TypeError):
        Stage() + 1

    # Pipeline
    with pytest.raises(TypeError):
        (Stage() + Stage()) + 1


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
        (1, 0, {"stage1": 1}),
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


@pytest.mark.parametrize(
    ("status", "out"),
    [
        (0, {"stage1": 0, "stage2": 0}),
        (1, {"stage1": 1}),
    ],
    ids=["requirements_met", "requirements_not_met"]
)
def test_pipeline_run_stage_requires_byid(status, out):
    """
    Test `requires`-property of `Stage` with reference as string identifier.
    """

    output = Pipeline(
        "a", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"stage1": status}),
            status=lambda **kwargs: status
        ),
        b=Stage(
            requires={"a": 0},
            action=lambda out, **kwargs: out.update({"stage2": 0})
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
def test_pipeline_run_stage_requires_byint(status, out):
    """
    Test `requires`-property of `Stage` with reference as integer.
    """

    output = Pipeline(
        "a", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"stage1": status}),
            status=lambda **kwargs: status
        ),
        b=Stage(
            requires={-1: 0},
            action=lambda out, **kwargs: out.update({"stage2": 0})
        ),
    ).run()

    assert output.data == out


def test_pipeline_run_stage_requires_exception_no_status():
    """
    Test `requires`-property of `Stage` with reference to not yet
    executed `Stage`
    """

    with pytest.raises(PipelineError):
        Pipeline(
            Stage(
                requires={Next: 1}
            ),
            Stage(),
        ).run()


def test_pipeline_run_stage_requires_exception_bad_type():
    """
    Test `requires`-property of `Stage` with reference to not yet
    executed `Stage`
    """

    with pytest.raises(PipelineError):
        Pipeline(
            Stage(
                requires={Next: 1}
            ),
            Fork(lambda **kwargs: None),
        ).run()


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
            action=lambda out, **kwargs: out.append("a")
        ),
        b=Stage(
            action=lambda out, **kwargs: out.append("b")
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
    assert len(output.records) == 3


# #############################
# ### Fork

def test_pipeline_fork_minimal():
    """
    Test class `Fork` with method `run` of class `Pipeline` for
    minimal setup.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"test": out["test"] + 1}),
        ),
        b=Stage(
            action=lambda out, **kwargs: out.update({"test": 0}),
        ),
        f=Fork(
            lambda out, **kwargs: "a" if out["test"] < 3 else "b"
        ),
        initialize_output=lambda: {"test": 0},
    ).run()

    assert len(output.records) == 4
    assert output.data["test"] == 0


def test_pipeline_fork_id():
    """
    Test property `id` of class `Fork` and its use in a `Pipeline.
    """

    f = Fork(
        lambda **kwargs: None
    )
    assert isinstance(f.id, str)
    assert f.id in Pipeline(f)


def test_pipeline_fork_kwargs():
    """
    Test class `Fork` with method `run` of class `Pipeline` for
    passing through kwargs.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda fork_value, **kwargs: fork_value
        ),
    ).run(fork_value=None)

    assert len(output.records) == 1


def test_pipeline_fork_exit():
    """
    Test exit via `Fork` with method `run` of class `Pipeline` for
    minimal setup.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"test": 1}),
        ),
        b=Stage(
            action=lambda out, **kwargs: out.update({"test": 0}),
        ),
        f=Fork(
            lambda **kwargs: None
        ),
    ).run()

    assert len(output.records) == 1
    assert output.data["test"] == 1


def test_pipeline_fork_stageref_int():
    """
    Test returning `StageRef` and `int` from `Fork`-conditional with
    method `run` of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"test": out["test"] + 1}),
        ),
        b=Stage(
            action=lambda out, **kwargs: out.update({"test": -1}),
        ),
        f=Fork(
            lambda out, **kwargs: Previous if out["test"] == 1 else 1
        ),
        initialize_output=lambda: {"test": 0}
    ).run()

    assert len(output.records) == 3
    assert output.data["test"] == -1


def test_pipeline_fork_stageref_first_last():
    """
    Test returning `First` and `Last` from `Fork`-conditional with
    method `run` of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(
            action=lambda out, **kwargs: out.update({"test": out["test"] + 1}),
        ),
        b=Stage(
            action=lambda out, **kwargs: out.update({"test": -1}),
        ),
        f=Fork(
            lambda out, **kwargs: First if out["test"] == 1 else Last
        ),
        initialize_output=lambda: {"test": 0}
    ).run()

    assert len(output.records) == 3
    assert output.data["test"] == -1


def test_pipeline_fork_stageref_next():
    """
    Test returning `Next` from `Fork`-conditional with method `run`
    of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda out, **kwargs: Next
        ),
    ).run()

    assert len(output.records) == 2


def test_pipeline_fork_stageref_skip():
    """
    Test returning `Skip` from `Fork`-conditional with method `run`
    of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda out, **kwargs: Skip
        ),
    ).run()

    assert len(output.records) == 1


def test_pipeline_fork_stageref_stagebyid():
    """
    Test returning `StageById` from `Fork`-conditional with method `run`
    of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda count, **kwargs: StageById("a") if count < 1 else None
        ),
    ).run()

    assert len(output.records) == 2


def test_pipeline_fork_stageref_stagebyindex():
    """
    Test returning `StageByIndex` from `Fork`-conditional with method `run`
    of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda count, **kwargs: StageByIndex(0) if count < 1 else None
        ),
    ).run()

    assert len(output.records) == 2


def test_pipeline_fork_stageref_stagebyincrement():
    """
    Test returning `StageByIncrement` from `Fork`-conditional with method `run`
    of class `Pipeline`.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(),
        b=Stage(),
        f=Fork(
            lambda count, **kwargs: StageByIncrement(-1) if count < 1 else None
        ),
    ).run()

    assert len(output.records) == 2


def test_fork_exception():
    """
    Test exception-behavior in method `run` of class `Pipeline` when
    using `Fork`s.
    """

    with pytest.raises(PipelineError):
        Pipeline(
            "a", "f",
            a=Stage(),
            f=Fork(
                lambda **kwargs: "b"
            ),
        ).run()


@pytest.mark.parametrize(
    ("status", "expectation"),
    [
        (0, 2),
        (1, 1)
    ],
)
def test_pipeline_fork_stagerecord_argument(status, expectation):
    """
    Test class `last_record`-argument passed to `Fork` with method `run`
    of class `Pipeline` for minimal setup.
    """

    output = Pipeline(
        "a", "f", "b",
        a=Stage(
            status=lambda **kwargs: status
        ),
        f=Fork(
            lambda records, **kwargs: Next if records[-1].status == 0 else None
        ),
        b=Stage(
            status=lambda **kwargs: 2
        ),
    ).run()

    assert output.last_status == expectation


# #############################
# ### Pipearray

def test_pipearray_run_positional():
    """Test method `run` of `Pipearray` with positional `Pipelines`."""

    pipeline_a = Pipeline(
        Stage(status=lambda **kwargs: 0)
    )
    pipeline_b = Pipeline(
        Stage(status=lambda **kwargs: 1)
    )

    output = Pipearray(pipeline_a, pipeline_b).run()

    assert isinstance(output, list)
    assert len(output) == 2
    for _output in output:
        assert isinstance(_output, PipelineOutput)
    assert output[0].records[0][1] == 0
    assert output[1].records[0][1] == 1


def test_pipearray_run_keyword():
    """Test method `run` of `Pipearray` with keyword arg `Pipelines`."""

    pipeline_a = Pipeline(
        Stage(status=lambda **kwargs: 0)
    )
    pipeline_b = Pipeline(
        Stage(status=lambda **kwargs: 1)
    )

    output = Pipearray(
        a=pipeline_a,
        b=pipeline_b
    ).run()

    assert isinstance(output, dict)
    assert len(output) == 2
    assert "a" in output
    assert "b" in output
    for _output in output.values():
        assert isinstance(_output, PipelineOutput)
    assert output["a"].records[0][1] == 0
    assert output["b"].records[0][1] == 1


def test_pipearray_run_mixed():
    """
    Test method `run` of `Pipearray` with mixed positional and keyword
    args `Pipelines`.
    """

    pipeline_a = Pipeline(
        Stage(status=lambda **kwargs: 0)
    )
    pipeline_b = Pipeline(
        Stage(status=lambda **kwargs: 1)
    )

    output = Pipearray(
        pipeline_a,
        b=pipeline_b
    ).run()

    assert isinstance(output, dict)
    assert len(output) == 2
    assert pipeline_a.id in output
    assert "b" in output
    for _output in output.values():
        assert isinstance(_output, PipelineOutput)
    assert output[pipeline_a.id].records[0][1] == 0
    assert output["b"].records[0][1] == 1


# #############################
# ### _StageRef

def test_previousn_error():
    """Test function `PreviousN` with bad argument."""

    with pytest.raises(ValueError):
        PreviousN(-1)


def test_nextn_error():
    """Test function `NextN` with bad argument."""

    with pytest.raises(ValueError):
        NextN(-1)


@pytest.mark.parametrize(
    "stageref",
    [
        Previous,
        First,
        Last,
        StageByIndex(1),
        StageById("a"),
        StageByIncrement(1),
        StageByIncrement(-1),
    ]
)
def test_previous_get_error(stageref):
    """Test method get for different `_StageRef`s with bad context."""

    with pytest.raises(PipelineError):
        stageref.get(PipelineContext([], 0, False, [], {}, {}, 0))


@pytest.mark.parametrize(
    "stageref",
    [
        Next,
        StageByIncrement(1),
        StageByIncrement(-3),
    ]
)
def test_next_loop(stageref):
    """Test method `get` for different `_StageRef`s in loop-context."""

    ref = stageref.get(PipelineContext(
        ["a", "b"], 1, True, [], {}, {}, 0)
    )

    assert ref.index == 0
