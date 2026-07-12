"""Test class `PipeArray`."""

from unittest import TestCase

from data_plumber import Pipearray, Pipeline, Stage
from data_plumber.output import PipelineOutput


class TestPipeArray(TestCase):
    """Test method `run` of class `PipeArray`."""

    def test_run_positional(self):
        """Test method `run` of `Pipearray` with positional `Pipelines`."""

        pipeline_a = Pipeline(
            Stage(status=lambda **kwargs: 0)
        )
        pipeline_b = Pipeline(
            Stage(status=lambda **kwargs: 1)
        )

        output = Pipearray(pipeline_a, pipeline_b).run()

        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 2)
        for _output in output:
            self.assertIsInstance(_output, PipelineOutput)
        self.assertEqual(output[0].records[0][1], 0)
        self.assertEqual(output[1].records[0][1], 1)

    def test_run_keyword(self):
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

        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), 2)
        self.assertIn("a", output)
        self.assertIn("b", output)
        for _output in output.values():
            self.assertIsInstance(_output, PipelineOutput)
        self.assertEqual(output["a"].records[0][1], 0)
        self.assertEqual(output["b"].records[0][1], 1)

    def test_run_mixed(self):
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

        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), 2)
        self.assertIn(pipeline_a.id, output)
        self.assertIn("b", output)
        for _output in output.values():
            self.assertIsInstance(_output, PipelineOutput)
        self.assertEqual(output[pipeline_a.id].records[0][1], 0)
        self.assertEqual(output["b"].records[0][1], 1)
