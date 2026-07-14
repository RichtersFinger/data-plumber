"""Test class `Pipeline`."""

from unittest import TestCase

from data_plumber import Pipeline, Stage, PipelineError, Fork


class TestPipelineRun(TestCase):
    """Test method `run` of class `Pipeline`."""

    def test_minimal(self):
        """Test for minimal setup."""

        output = Pipeline(
            Stage(action=lambda out, **kwargs: out.update({"test": 0})),
        ).run()

        self.assertIn("test", output.data)
        self.assertEqual(output.data["test"], 0)

    def test_minimal_two_stage(self):
        """Test for minimal two-stage setup."""

        output = Pipeline(
            Stage(action=lambda out, **kwargs: out.update({"stage1": 0})),
            Stage(action=lambda out, **kwargs: out.update({"stage2": 0})),
        ).run()

        self.assertIn("stage1", output.data)
        self.assertEqual(output.data["stage1"], 0)
        self.assertIn("stage2", output.data)
        self.assertEqual(output.data["stage2"], 0)

    def test_minimal_pass_through(self):
        """Test pass through of kwargs in minimal setup."""

        test_arg0 = 0

        output = Pipeline(
            Stage(
                action=lambda out, test_arg, **kwargs: out.update(
                    {"test": test_arg}
                )
            ),
            Stage(
                action=lambda out, **kwargs: out.update(
                    {"test2": kwargs["test_arg"]}
                )
            ),
        ).run(test_arg=test_arg0)

        self.assertIn("test", output.data)
        self.assertEqual(output.data["test"], test_arg0)
        self.assertEqual(output.data["test2"], test_arg0)

    def test_minimal_export(self):
        """Test exporting additional kwargs from `Stage`."""

        test_arg0 = 1

        output = Pipeline(
            Stage(  # export kwarg
                export=lambda **kwargs: {"new_kw": test_arg0}
            ),
            Stage(  # write that kwarg into output.data
                action=lambda out, new_kw, **kwargs: out.update(
                    {"new_kw": new_kw}
                )
            ),
        ).run()

        self.assertIn("new_kw", output.data)
        self.assertEqual(output.data["new_kw"], test_arg0)

    def test_reserved_kwargs(self):
        """Test exception behavior for reserved keywords."""

        for kwarg in ["out", "primer", "status", "count"]:
            with self.subTest(kwarg, kwarg=kwarg):
                with self.assertRaises(PipelineError):
                    Pipeline(
                        Stage(),
                    ).run(**{kwarg: 0})

    def test_run_initialize_output(self):
        """
        Test property `initialize_output` with method `run`.
        """

        output = Pipeline(
            Stage(
                action=lambda out, **kwargs: out.append(0),
                status=lambda **kwargs: 0,
            ),
            initialize_output=lambda: [],
        ).run()

        self.assertIsInstance(output.data, list)
        self.assertEqual(len(output.data), 1)
        self.assertEqual(output.data[0], 0)


class TestPipelineRunForKwargs(TestCase):
    """Test decorator `run_for_kwargs` of class `Pipeline`."""

    def test_minimal(self):
        """Test minimal."""

        pipeline = Pipeline(
            Stage(
                action=lambda out, outer_arg, **kwargs: out.update(
                    {"arg": outer_arg}
                )
            ),
        )

        @pipeline.run_for_kwargs(outer_arg=0)
        def f(arg=None):
            return arg

        self.assertEqual(f(), 0)

    def test_partial_generation_of_kwargs(self):
        """Test only partial generation of kwargs from pipeline."""

        pipeline = Pipeline(
            Stage(
                action=lambda out, outer_arg, **kwargs: out.update(
                    {"arg1": outer_arg}
                )
            ),
        )

        @pipeline.run_for_kwargs(outer_arg=0)
        def f(arg1=None, arg2=None):
            return arg1, arg2

        self.assertTupleEqual(f(arg2=1), (0, 1))

    def test_multiple_priority(self):
        """Test priority of kwargs."""

        pipeline = Pipeline(
            Stage(
                action=lambda out, outer_arg, **kwargs: out.update(
                    {"arg1": outer_arg}
                )
            ),
        )

        @pipeline.run_for_kwargs(outer_arg=0)
        def f(arg1=None, arg2=None):
            return arg1, arg2

        self.assertTupleEqual(f(arg1=2, arg2=1), (2, 1))


class TestPipelineFinalizeOutput(TestCase):
    """Test argument `finalize_output` of `Pipeline.run`."""

    def test_minimal(self):
        """Test minimal."""

        output = Pipeline(
            Stage(), finalize_output=lambda data, **kwargs: data.update(kwargs)
        ).run(finalizer="finalizer")

        self.assertIn("finalizer", output.data)
        self.assertEqual(output.data["finalizer"], "finalizer")

    def test_output_override(self):
        """Test output override."""

        output = Pipeline(
            Stage(), finalize_output=lambda data, **kwargs: data.update(kwargs)
        ).run(
            finalizer="finalizer",
            finalize_output=lambda data, **kwargs: data.update(
                {"finalizer-override": True}
            ),
        )

        self.assertNotIn("finalizer", output.data)
        self.assertIn("finalizer-override", output.data)
        self.assertTrue(output.data["finalizer-override"])

    def test_finalize_using_records(self):
        """Test using `records` during finalize."""

        for status, expected_out in [
            (0, {"status": 0}),
            (1, {}),
        ]:
            with self.subTest(status=status, expected_out=expected_out):
                output = Pipeline(
                    Stage(status=lambda status=status, **kwargs: status),
                    finalize_output=lambda data, records, **kwargs: (
                        data.update({"status": 0})
                        if records[-1].status == 0
                        else None
                    ),
                ).run()

                self.assertDictEqual(output.data, expected_out)

    def test_finalize_using_records_during_run(self):
        """Test `finalize_output` passed during `run`."""

        for status, expected_out in [
            (0, {"status": 0}),
            (1, {}),
        ]:
            with self.subTest(status=status, expected_out=expected_out):
                output = Pipeline(
                    Stage(status=lambda status=status, **kwargs: status),
                ).run(
                    finalize_output=lambda data, records, **kwargs: (
                        data.update({"status": 0})
                        if records[-1].status == 0
                        else None
                    )
                )

                self.assertDictEqual(output.data, expected_out)


class TestPipelineExitOnStatus(TestCase):
    """Test `Pipeline` property `exit_on_status`."""

    def test_scalar_status(self):
        """Test `Pipeline.run` with scalar `exit_on_status`."""

        output = Pipeline(
            Stage(
                action=lambda out, **kwargs: out.update({"stage1": 1}),
                status=lambda **kwargs: 1,
            ),
            Stage(action=lambda out, **kwargs: out.update({"stage2": 0})),
            exit_on_status=1,
        ).run()

        self.assertDictEqual(output.data, {"stage1": 1})

    def test_status_callable(self):
        """Test `Pipeline.run` with callable `exit_on_status`."""

        output = Pipeline(
            Stage(
                action=lambda out, **kwargs: out.update({"stage1": 1}),
                status=lambda **kwargs: 1,
            ),
            Stage(action=lambda out, **kwargs: out.update({"stage2": 0})),
            exit_on_status=lambda status: status > 0,
        ).run()

        self.assertDictEqual(output.data, {"stage1": 1})


class TestPipelineLength(TestCase):
    """Test `Pipeline` length calculation."""

    def test_single_stage(self):
        """Test single stage."""

        pipeline = Pipeline(
            Stage(),
        )

        self.assertEqual(len(pipeline), 1)

    def test_two_stages(self):
        """Test two stages."""

        pipeline = Pipeline(
            Stage(),
            Stage(),
        )

        self.assertEqual(len(pipeline), 2)


class TestPipelineExtension(TestCase):
    """Test methods to extend existing `Pipeline`."""

    @staticmethod
    def _run_parameterized(callback):
        def decorated(self):
            for stage_or_pipeline in [
                Stage(action=lambda out, **kwargs: out.append(1)),
                Pipeline(
                    Stage(action=lambda out, **kwargs: out.append(1)),
                ),
            ]:
                with self.subTest(stage_or_pipeline=stage_or_pipeline):
                    callback(self, stage_or_pipeline)

        return decorated

    @_run_parameterized
    def test_append(self, stage_or_pipeline):
        """Test method `Pipeline.append`."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(0)),
            initialize_output=lambda: [],
        )

        self.assertEqual(len(pipeline), 1)

        pipeline.append(stage_or_pipeline)

        self.assertEqual(len(pipeline), 2)

        output = pipeline.run()

        self.assertListEqual(output.data, [0, 1])

    @_run_parameterized
    def test_prepend(self, stage_or_pipeline):
        """Test method `Pipeline.prepend`."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(0)),
            initialize_output=lambda: [],
        )

        self.assertEqual(len(pipeline), 1)

        pipeline.prepend(stage_or_pipeline)

        self.assertEqual(len(pipeline), 2)

        output = pipeline.run()

        self.assertListEqual(output.data, [1, 0])

    @_run_parameterized
    def test_insert(self, stage_or_pipeline):
        """Test method `Pipeline.insert`."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(0)),
            initialize_output=lambda: [],
        )

        self.assertEqual(len(pipeline), 1)

        pipeline.insert(0, stage_or_pipeline)
        pipeline.insert(2, stage_or_pipeline)

        self.assertEqual(len(pipeline), 3)

        output = pipeline.run()

        self.assertListEqual(output.data, [1, 0, 1])

    def test_append_named(self):
        """Test method `Pipeline.append` with named `Stage`s."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(1)),
            initialize_output=lambda: [],
        )

        pipeline.append(
            "a",
            a=Stage(action=lambda out, **kwargs: out.append(0)),
        )

        self.assertListEqual(pipeline.run().data, [1, 0])

    def test_prepend_named(self):
        """Test method `Pipeline.prepend` with named `Stage`s."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(1)),
            initialize_output=lambda: [],
        )

        pipeline.prepend(
            "a",
            a=Stage(action=lambda out, **kwargs: out.append(0)),
        )

        self.assertListEqual(pipeline.run().data, [0, 1])

    def test_insert_named(self):
        """Test method `Pipeline.insert` with named `Stage`s."""

        pipeline = Pipeline(
            Stage(action=lambda out, **kwargs: out.append(1)),
            initialize_output=lambda: [],
        )

        pipeline.insert(
            0,
            "a",
            a=Stage(action=lambda out, **kwargs: out.append(0)),
        )

        self.assertListEqual(pipeline.run().data, [0, 1])


class TestPipelineUnpacking(TestCase):
    """Test unpacking behavior of `Pipeline` objects."""

    def test_unpacking(self):
        """Test method `__iter__` for class `Pipeline`."""

        stage_a = Stage()
        stage_b = Stage()

        pipeline = Pipeline(stage_a, stage_b)

        pipeline2 = Pipeline(*pipeline)

        self.assertEqual(len(pipeline2), 2)

        x, y = pipeline

        self.assertEqual(x, stage_a)
        self.assertEqual(y, stage_b)

    def test_unpacking_mapping(self):
        """Test method `__iter__` for class `Pipeline`."""

        stage_a = Stage(action=lambda out, **kwargs: out.append("stage_a"))
        stage_b = Stage(action=lambda out, **kwargs: out.append("stage_b"))

        pipeline = Pipeline("a", "b", a=stage_a, b=stage_b)

        output = Pipeline(
            "b", "a", **pipeline, initialize_output=lambda: []
        ).run()

        self.assertListEqual(output.data, ["stage_b", "stage_a"])


class TestPipelineEmptyComponent(TestCase):
    """Test `Pipeline.run` for empty `PipelineComponent`."""

    def test_empty_component(self):
        """
        Test empty `PipelineComponent` behavior in `Pipeline.run`.
        """

        output = Pipeline(Stage(), "empty_component").run()

        self.assertEqual(len(output.records), 1)

    def test_fork_empty_component(self):
        """
        Test returning string-id of empty `PipelineComponent` from `Fork`-
        conditional in `Pipeline.run`.
        """

        output = Pipeline(
            Fork(lambda **kwargs: "fork_target"),
            Stage(),
            "fork_target",
            Stage(),
        ).run()

        self.assertEqual(len(output.records), 1)


class TestPipelineStageAddition(TestCase):
    """Test addition of `Stage`s to `Pipeline`."""

    def test_stage_addition(self):
        """Test method `__add__` for class `Stage`."""

        stage_a = Stage(
            action=lambda out, **kwargs: out.update({"stage_a": 0})
        )
        stage_b = Stage(
            action=lambda out, **kwargs: out.update({"stage_b": 0})
        )
        pipeline = stage_a + stage_b

        self.assertIsInstance(pipeline, Pipeline)

        output = pipeline.run()

        self.assertDictEqual(output.data, {"stage_a": 0, "stage_b": 0})

    def test_stage_addition_multiple(self):
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

        self.assertIsInstance(pipeline_a, Pipeline)
        self.assertIsInstance(pipeline_b, Pipeline)
        self.assertIsInstance(pipeline_c, Pipeline)

        output_a = pipeline_a.run()
        output_b = pipeline_b.run()
        output_c = pipeline_c.run()

        self.assertDictEqual(
            output_a.data, {"stage_a": 0, "stage_b": 0, "stage_c": 0}
        )
        self.assertDictEqual(
            output_b.data, {"stage_a": 0, "stage_b": 0, "stage_c": 0}
        )
        self.assertDictEqual(output_c.data, {"stage_a": 0, "stage_b": 0})
        self.assertEqual(len(output_c.records), 4)

    def test_stage_addition_exception(self):
        """
        Test method `__add__` for classes `Stage`/`Pipeline` with bad
        types.
        """

        # Stage
        self.assertRaises(TypeError, lambda: Stage() + 1)

        # Pipeline
        self.assertRaises(TypeError, lambda: (Stage() + Stage()) + 1)


class TestPipelineNamedStages(TestCase):
    """Test named `Stage`s in `Pipeline`."""

    def test_minimal(self):
        """Test minimal setup."""

        output = Pipeline(
            "a",
            a=Stage(
                action=lambda out, **kwargs: out.update({"test": 0})
            ),
        ).run()

        self.assertIn("test", output.data)
        self.assertEqual(output.data["test"], 0)

    def test_execution_order(self):
        """Test execution order."""

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

        self.assertListEqual(output.data, ["a", "b", "a"])


class TestPipelineLoop(TestCase):
    """Test loop-functionality of `Pipeline`."""

    def test_minimal(self):
        """Test minimal setup."""

        output = Pipeline(
            Stage(
                action=lambda out, **kwargs: out.update({"test": out["test"] + 1}),
                status=lambda out, **kwargs: 0 if out["test"] < 3 else 1,
            ),
            initialize_output=lambda: {"test": 0},
            exit_on_status=1,
            loop=True,
        ).run()

        self.assertIn("test", output.data)
        self.assertEqual(output.data["test"], 3)
        self.assertEqual(len(output.records), 3)
