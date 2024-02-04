### Overview

[Documentation](../README.md#documentation)

`data_plumber` is designed to provide a framework for flexible data-processing based on re-usable building blocks.

At its core stands the class `Pipeline` which can be understood as both a container for a collection of instructions (`PipelineComponent`) and an interface for the execution of a process (`Pipeline.run(...)`).
Previously defined `Pipeline`s can be recombined with other `Pipelines` or extended by individual `PipelineComponents`. Individual `Pipeline.run`s can be triggered with run-specific arguments.

`PipelineComponents` are either units defining actual data-processing (`Stage`) or control the flow of a `Pipeline` execution (`Fork`). Until a `Fork` is encountered, a `Pipeline.run` iterates a pre-configured list of `PipelineComponent`s. Any `Stage`-type component provides an integer status value after execution which is then available for defining conditional execution of `Stage`s or changes in flow (`Fork`).

A `Stage` itself consists of multiple (generally optional) highly customizable sub-stages and propertis that can be configured at instantiation. In particular, a versatile referencing system based on (pre-defined) `StageRef`-type classes can be used to define the requirements for `Stage`s. Similarly, this system is also used by `Fork`s.

The output of a `Pipeline.run` is of type `PipelineOutput`. It contains extensive information on the order of operations, the response from individual `Stage`s, and a `data`-property (of customizable type). The latter can be used to store and/or output processed data from the `Pipeline`'s execution context.

Finally, aside from recombination of `Pipeline`s into more complex `Pipeline`s, multiple instances of `Pipeline`s can be pooled into a `Pipearray`. This construct allows to call different `Pipeline`s with identical input data.
