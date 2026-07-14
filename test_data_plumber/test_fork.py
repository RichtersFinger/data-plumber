"""Test class `Fork`."""

from unittest import TestCase

from data_plumber import (
    Pipeline,
    Stage,
    PipelineError,
    Fork,
    Previous,
    Next,
    First,
    Last,
    Skip,
    StageByIndex,
    StageById,
    StageByIncrement,
)


class TestFork(TestCase):
    """Test class `Fork`."""

    def test_minimal(self):
        """Test minimal setup."""

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(
                action=lambda out, **kwargs: out.update(
                    {"test": out["test"] + 1}
                ),
            ),
            b=Stage(
                action=lambda out, **kwargs: out.update({"test": 0}),
            ),
            f=Fork(lambda out, **kwargs: "a" if out["test"] < 3 else "b"),
            initialize_output=lambda: {"test": 0},
        ).run()

        self.assertEqual(len(output.records), 4)
        self.assertEqual(output.data["test"], 0)

    def test_id(self):
        """
        Test property `id` of class `Fork` and its use in a `Pipeline.
        """

        f = Fork(lambda **kwargs: None)
        self.assertIsInstance(f.id, str)
        self.assertIn(f.id, Pipeline(f))

    def test_kwargs(self):
        """
        Test class `Fork` with method `run` of class `Pipeline` for
        passing through kwargs.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(lambda fork_value, **kwargs: fork_value),
        ).run(fork_value=None)

        self.assertEqual(len(output.records), 1)

    def test_exit(self):
        """
        Test exit via `Fork` with method `run` of class `Pipeline` for
        minimal setup.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(
                action=lambda out, **kwargs: out.update({"test": 1}),
            ),
            b=Stage(
                action=lambda out, **kwargs: out.update({"test": 0}),
            ),
            f=Fork(lambda **kwargs: None),
        ).run()

        self.assertEqual(len(output.records), 1)
        self.assertEqual(output.data["test"], 1)

    def test_stageref_int(self):
        """
        Test returning `StageRef` and `int` from `Fork`-conditional with
        method `run` of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(
                action=lambda out, **kwargs: out.update(
                    {"test": out["test"] + 1}
                ),
            ),
            b=Stage(
                action=lambda out, **kwargs: out.update({"test": -1}),
            ),
            f=Fork(lambda out, **kwargs: Previous if out["test"] == 1 else 1),
            initialize_output=lambda: {"test": 0},
        ).run()

        self.assertEqual(len(output.records), 3)
        self.assertEqual(output.data["test"], -1)

    def test_stageref_first_last(self):
        """
        Test returning `First` and `Last` from `Fork`-conditional with
        method `run` of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(
                action=lambda out, **kwargs: out.update(
                    {"test": out["test"] + 1}
                ),
            ),
            b=Stage(
                action=lambda out, **kwargs: out.update({"test": -1}),
            ),
            f=Fork(lambda out, **kwargs: First if out["test"] == 1 else Last),
            initialize_output=lambda: {"test": 0},
        ).run()

        self.assertEqual(len(output.records), 3)
        self.assertEqual(output.data["test"], -1)

    def test_stageref_next(self):
        """
        Test returning `Next` from `Fork`-conditional with method `run`
        of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(lambda out, **kwargs: Next),
        ).run()

        self.assertEqual(len(output.records), 2)

    def test_stageref_skip(self):
        """
        Test returning `Skip` from `Fork`-conditional with method `run`
        of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(lambda out, **kwargs: Skip),
        ).run()

        self.assertEqual(len(output.records), 1)

    def test_stageref_stagebyid(self):
        """
        Test returning `StageById` from `Fork`-conditional with method `run`
        of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(
                lambda count, **kwargs: StageById("a") if count < 1 else None
            ),
        ).run()

        self.assertEqual(len(output.records), 2)

    def test_stageref_stagebyindex(self):
        """
        Test returning `StageByIndex` from `Fork`-conditional with method `run`
        of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(
                lambda count, **kwargs: StageByIndex(0) if count < 1 else None
            ),
        ).run()

        self.assertEqual(len(output.records), 2)

    def test_stageref_stagebyincrement(self):
        """
        Test returning `StageByIncrement` from `Fork`-conditional with method
        `run` of class `Pipeline`.
        """

        output = Pipeline(
            "a",
            "f",
            "b",
            a=Stage(),
            b=Stage(),
            f=Fork(
                lambda count, **kwargs: (
                    StageByIncrement(-1) if count < 1 else None
                )
            ),
        ).run()

        self.assertEqual(len(output.records), 2)

    def test_fork_exception(self):
        """
        Test exception-behavior in method `run` of class `Pipeline` when
        using `Fork`s.
        """

        self.assertRaises(
            PipelineError,
            Pipeline(
                "a",
                "f",
                a=Stage(),
                f=Fork(lambda **kwargs: "b"),
            ).run,
        )

    def test_stagerecord_argument(self):
        """
        Test class `last_record`-argument passed to `Fork` with method `run`
        of class `Pipeline` for minimal setup.
        """

        for status, expectation in [(0, 2), (1, 1)]:
            with self.subTest(status=status, expectation=expectation):
                output = Pipeline(
                    "a",
                    "f",
                    "b",
                    a=Stage(
                        status=lambda test_value_status=status, **kwargs: test_value_status
                    ),
                    f=Fork(
                        lambda records, **kwargs: (
                            Next if records[-1].status == 0 else None
                        )
                    ),
                    b=Stage(status=lambda **kwargs: 2),
                ).run()

                self.assertEqual(output.last_status, expectation)
