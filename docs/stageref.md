### StageRef

[Documentation](../README.md#documentation)

`StageRef`s can be utilized in the context of requirements of `Stage`s as well as flow control with `Fork`s.
While additional types of `StageRef`s can be defined, `data_plumber` already provides rich possibilities natively.

There are two different categories of `StageRef`s:
1. referring to records of previously executed `PipelineComponents` (a record then provides information on the components position in the `Pipeline`'s sequence of components)
1. referring to a component within the list of registered components of a `Pipeline`

#### List of predefined StageRefs (by record)
* **First**: record of first component
* **Previous**: record of previous component (one step)
* **PreviousN(n)**: record of previous component (`n` steps)

#### List of predefined StageRefs (by sequence)
* **Last**: last component in sequence
* **Next**: next component in sequence (one step)
* **Skip**: component after next in sequence (two steps)
* **NextN(n)**: next component (`n` steps)
* **StageById(id)**: first occurrence of `id` in sequence
* **StageByIndex(index)**: component at `index` of sequence
* **StageByIncrement(n)**: component with relative position `n` in sequence

#### Example
```
>>> from data_plumber import Pipeline, Stage, Fork, Previous, NextN
>>> output = Pipeline(
        Stage(
            status=lambda **kwargs: 0
        ),
        Stage(
            requires={Previous: 0},
            status=lambda count, **kwargs: count
        ),
        Fork(
            lambda count, **kwargs: NextN(1)
        ),
        exit_on_status=lambda status: status > 3,
        loop=True
    ).run()
>>> len(output.records)
6
```