"""Test class `Stage`."""

from unittest import TestCase

from data_plumber import (
    Pipeline,
    PipelineError,
    Stage,
    Previous,
    First,
    Next,
    Fork,
)


class TestStagePrimer(TestCase):
    """Test `Stage.primer`."""

    def test_stage_primer_minimal(self):
        """Test property `primer` of class `Stage` for minimal setup."""

        output = Pipeline(
            Stage(
                primer=lambda **kwargs: "primer",
                action=lambda out, primer, **kwargs: out.update(
                    {"test": primer}
                ),
            ),
        ).run()

        self.assertIn("test", output.data)
        self.assertEqual(output.data["test"], "primer")


class TestStageRequires(TestCase):
    """Test `Stage.requires`."""

    def test_requires_previous(self):
        """
        Test `requires`-property of `Stage` with `Previous`.
        """

        for id_, status1, status2, out in [
            (
                "requirements_met",
                0,
                0,
                {"stage1": 0, "stage2": 0, "stage3": 0},
            ),
            ("requirements_not_met_1", 1, 0, {"stage1": 1}),
            ("requirements_not_met_2", 0, 1, {"stage1": 0, "stage2": 1}),
            ("requirements_not_met_12", 1, 1, {"stage1": 1}),
        ]:
            with self.subTest(id_, status1=status1, status2=status2, out=out):
                output = Pipeline(
                    Stage(
                        action=lambda out, test_value_status1=status1, **kwargs: out.update(
                            {"stage1": test_value_status1}
                        ),
                        status=lambda test_value_status1=status1, **kwargs: test_value_status1,
                    ),
                    Stage(
                        requires={Previous: 0},
                        action=lambda out, test_value_status2=status2, **kwargs: out.update(
                            {"stage2": test_value_status2}
                        ),
                        status=lambda test_value_status2=status2, **kwargs: test_value_status2,
                    ),
                    Stage(
                        requires={Previous: 0},
                        action=lambda out, **kwargs: out.update({"stage3": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_first(self):
        """
        Test `requires`-property of `Stage` with `First`.
        """

        for id_, status, out in [
            ("requirements_met", 0, {"stage1": 0, "stage2": 0, "stage3": 0}),
            ("requirements_not_met", 1, {"stage1": 1}),
        ]:
            with self.subTest(id_, status=status, out=out):
                output = Pipeline(
                    Stage(
                        action=lambda out, test_value_status=status, **kwargs: out.update(
                            {"stage1": test_value_status}
                        ),
                        status=lambda test_value_status=status, **kwargs: test_value_status,
                    ),
                    Stage(
                        requires={First: 0},
                        action=lambda out, **kwargs: out.update({"stage2": 0}),
                    ),
                    Stage(
                        requires={First: 0},
                        action=lambda out, **kwargs: out.update({"stage3": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_multiple(self):
        """
        Test `requires`-property of `Stage` with multiple requirements.
        """

        for id_, status, out in [
            ("requirements_met", 0, {"stage1": 0, "stage2": 0, "stage3": 0}),
            ("requirements_not_met", 1, {"stage1": 1, "stage2": 0}),
        ]:
            with self.subTest(id_, status=status, out=out):
                output = Pipeline(
                    Stage(
                        action=lambda out, test_value_status=status, **kwargs: out.update(
                            {"stage1": test_value_status}
                        ),
                        status=lambda test_value_status=status, **kwargs: test_value_status,
                    ),
                    Stage(
                        action=lambda out, **kwargs: out.update({"stage2": 0})
                    ),
                    Stage(
                        requires={First: 0, Previous: 0},
                        action=lambda out, **kwargs: out.update({"stage3": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_callable(self):
        """
        Test `requires`-property of `Stage` with callable requirement.
        """

        for id_, status, out in [
            ("requirements_met", 0, {"stage1": 0, "stage2": 0}),
            ("requirements_not_met", 1, {"stage1": 1}),
        ]:
            with self.subTest(id_, status=status, out=out):
                output = Pipeline(
                    Stage(
                        action=lambda out, test_value_status=status, **kwargs: out.update(
                            {"stage1": test_value_status}
                        ),
                        status=lambda test_value_status=status, **kwargs: test_value_status,
                    ),
                    Stage(
                        requires={First: (lambda status: status != 1)},
                        action=lambda out, **kwargs: out.update({"stage2": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_byid(self):
        """
        Test `requires`-property of `Stage` with reference as string identifier.
        """

        for id_, status, out in [
            ("requirements_met", 0, {"stage1": 0, "stage2": 0}),
            ("requirements_not_met", 1, {"stage1": 1}),
        ]:
            with self.subTest(id_, status=status, out=out):
                output = Pipeline(
                    "a",
                    "b",
                    a=Stage(
                        action=lambda out, test_value_status=status, **kwargs: out.update(
                            {"stage1": test_value_status}
                        ),
                        status=lambda test_value_status=status, **kwargs: test_value_status,
                    ),
                    b=Stage(
                        requires={"a": 0},
                        action=lambda out, **kwargs: out.update({"stage2": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_byint(self):
        """
        Test `requires`-property of `Stage` with reference as integer.
        """

        for id_, status, out in [
            ("requirements_met", 0, {"stage1": 0, "stage2": 0}),
            ("requirements_not_met", 1, {"stage1": 1}),
        ]:
            with self.subTest(id_, status=status, out=out):
                output = Pipeline(
                    "a",
                    "b",
                    a=Stage(
                        action=lambda out, test_value_status=status, **kwargs: out.update(
                            {"stage1": test_value_status}
                        ),
                        status=lambda test_value_status=status, **kwargs: test_value_status,
                    ),
                    b=Stage(
                        requires={-1: 0},
                        action=lambda out, **kwargs: out.update({"stage2": 0}),
                    ),
                ).run()

                self.assertDictEqual(output.data, out)

    def test_requires_exception_no_status(self):
        """
        Test `requires`-property of `Stage` with reference to not yet
        executed `Stage`
        """

        self.assertRaises(
            PipelineError,
            Pipeline(
                Stage(requires={Next: 1}),
                Stage(),
            ).run,
        )

    def test_requires_exception_bad_type(self):
        """
        Test `requires`-property of `Stage` with reference to not yet
        executed `Stage`
        """

        self.assertRaises(
            PipelineError,
            Pipeline(
                Stage(requires={Next: 1}),
                Fork(lambda **kwargs: None),
            ).run,
        )
