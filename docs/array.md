### Pipearray

[Documentation](../README.md#documentation)

A `Pipearray` is a convenience class that offers to run multiple `Pipeline`s based on the same input data.
Just like the `Pipeline`s themselves, the `Pipearray` can be either anonymous or named, depending on the use of positional and keyword arguments during setup.
The return type can then be either a list (only positional arguments) or a dictionary with keys being names/ids (at least one named `Pipeline`). Both contain the `PipelineOutput` objects of the individual `Pipeline`s.

#### Example
```
>>> from data_plumber import Pipeline, Pipearray
>>> Pipearray(Pipeline(...), Pipeline(...)).run(...)
<list[PipelineOutput]>
>>> Pipearray(
...   p=Pipeline(...),
...   q=Pipeline(...)
... ).run(...)
<dict[str, PipelineOutput]>
```