"""Test class `PipelineOutput`."""

from unittest import TestCase

from data_plumber import Pipeline, Stage


class TestPipelineOutput(TestCase):
    """Test class `PipelineOutput`."""

    def test_members(self):
        """Test class members."""

        output = Pipeline(
            Stage(
                action=lambda out, **kwargs: out.update({"test": 0}),
                status=lambda **kwargs: 0,
                message=lambda **kwargs: "stage 1",
            ),
        ).run(input="input")

        self.assertTrue(hasattr(output, "records"))
        self.assertTrue(hasattr(output, "kwargs"))
        self.assertTrue(hasattr(output, "data"))
        self.assertTrue(hasattr(output, "last_record"))
        self.assertTrue(hasattr(output, "last_message"))
        self.assertTrue(hasattr(output, "last_status"))

        self.assertTrue(isinstance(output.records, list))
        self.assertEqual(len(output.records), 1)
        self.assertEqual(output.records[0], ("stage 1", 0))
        self.assertEqual(output.last_record, ("stage 1", 0))
        self.assertTupleEqual(
            (output.last_message, output.last_status),
            ("stage 1", 0),
        )
        self.assertIsInstance(output.data, dict)
        self.assertDictEqual(output.data, {"test": 0})
        self.assertIsInstance(output.kwargs, dict)
        self.assertDictEqual(output.kwargs, {"input": "input"})

    def test_two_stage(self):
        """Test two-`Stage` setup."""

        output = Pipeline(
            Stage(
                status=lambda **kwargs: 0, message=lambda **kwargs: "stage 1"
            ),
            Stage(
                status=lambda **kwargs: 1, message=lambda **kwargs: "stage 2"
            ),
        ).run()

        self.assertEqual(len(output.records), 2)
        self.assertEqual(output.records[0], ("stage 1", 0))
        self.assertEqual(output.records[1], ("stage 2", 1))

    def test_pipeline_output_empty(self):
        """Test `PipelineOutput.last_X` in case of empty output."""

        output = Pipeline().run()

        self.assertIsNone(output.last_message)
        self.assertIsNone(output.last_status)
        self.assertIsNone(output.last_record)
