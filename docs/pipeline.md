### Pipeline

[Documentation](../README.md#documentation)

#### Building anonymous Pipelines

A `Pipeline` can be created in an empty, a partially, or a fully assembled state.

For the empty `Pipeline` a simple expression like
```
>>> from data_plumber import Pipeline, Stage
>>> Pipeline()
<data_plumber.pipeline.Pipeline object at ...>
```
suffices. Following up with statements like
```
>>> p = Pipeline()
>>> p.append(Stage())
>>> p.prepend(Pipeline())
>>> p.insert(Stage(), 1)
```
or simply by using the `+`-operator
```
>>> p = Pipeline()
>>> Stage() + p + Pipeline()
<data_plumber.pipeline.Pipeline object at ...>
```
Note that when adding to existing `Pipeline`s, the change is made in-place.
```
>>> p = Pipeline(Stage())
>>> len(p)
1
>>> p + Stage()
<data_plumber.pipeline.Pipeline object at ...>
>>> len(p)
2
```
Consequently, only properties of the first argument are inherited (refer to python's operator precedence).
Therefore, the use of this operation in combination with `Pipeline`s requires caution.

#### Building named Pipelines
Instead of giving the individual `PipelineComponents` as positional arguments during instantiation, they can be assigned names by providing components as keyword arguments (kwargs).
In addition to the kwargs, the positional arguments are still required to determine the order of operations for the `Pipeline`.
These are then given by the `PipelineComponent`'s name:
```
>>> Pipeline(
...   "a", "b", "a", "c",
...   a=Stage(...,),
...   b=Stage(...,),
...   c=Stage(...,)
... )
<data_plumber.pipeline.Pipeline object at ...>
```
In the example above, the `Pipeline` executes the `Stage`s in the order of `a > b > a > c` (note that the names of `Stage`s can occur multiple times in the positional arguments or via `Pipeline`-extending methods).
Methods like `Pipeline.append` also accept string identifiers for `PipelineComponents`.
If none are provided at instantiation, an internally generated identifier is used.

The two approaches of anonymous and named `Pipeline`s can be combined freely:
```
>>> Pipeline(
...   "a", Stage(...,), "a", "c",
...   a=Stage(...,),
...   c=Stage(...,)
... )
<data_plumber.pipeline.Pipeline object at ...>
```

Also note that empty `PipelineComponent` can be used as well.
This can be helpful to label certain points in a `Pipeline` without changing its behavior.
Consider for example a `Fork` needs to point to a specific part of a `Pipeline` but otherwise no named `PipelineComponent` are required:
```
>>> Pipeline(
...   Stage(...,),  # stage 1
...   Fork(
...     lambda **kwargs: "target_position"
...   ),
...   Stage(...,),  # stage 2
...   "target_position",
...   Stage(...,)   # stage 3,
...   ...
... )
<data_plumber.pipeline.Pipeline object at ...>
```
which when triggered executes the `Stage`s as 'stage 1' > 'stage 3' (the associated `PipelineOutput` does not contain any record of the empty component `"target_position"`).

#### Unpacking Pipelines
`Pipeline`s support unpacking to be used as, for example, positional or keyword arguments in the constructor of another `Pipeline`:
```
>>> p = Pipeline("a", ..., a=Stage(), ...)
>>> Pipeline("b", *p, ..., b=Stage(), **p, ...)
<data_plumber.pipeline.Pipeline object at ...>
```

#### Running a Pipeline
A `Pipeline` can be triggered by calling the `run`-method.
```
>>> Pipeline(...).run(...)
PipelineOutput(...)
```
Passing the `finalize_output` keyword argument into a `run` allows to modify the persistent `Pipeline`-data at exit (see section [Pipeline settings](#pipeline-settings) for details).
Any kwargs passed to this function are forwarded to its `PipelineComponent`'s `Callable`s.
Note that some keywords are reserved (`out`, `primer`, `status`, `count`, and `records`).

While `Fork`s are simply evaluated and their returned `StageRef` is used to find the next target for execution, `Stage`s have themselves multiple sub-stages.
First, the `Pipeline` checks the `Stage`'s requirements, then executions its `primer` before running the `action`-command.
Next, any `export`ed kwargs are updated in the `Pipeline.run` and, finally, the `status` and `response` message is generated (see `Stage` for details).

#### Pipeline settings
A `Pipeline` can be configured with multiple properties at instantiation:
* **initialize_output**: a `Callable` that returns an object which is consequently passed forward into the `PipelineComponent`'s `Callable`s; this object is refered to as "persistent data-object" (default generates an empty dictionary)
* **finalize_output**: a `Callable` that is called before (normally) exiting the `Pipeline.run` with the `run`'s kwargs as well as the persistent data-object and a list of previous `StageRecords` called `records` (can be overridden in call of `Pipeline.run`)
* **exit_on_status**: either integer value (`Pipeline` exists normally if any component returns this status) or a `Callable` that is called after any component with the component's status (if it evaluates to `True`, the `Pipeline.run` is stopped)
* **loop**: boolean; if `False`, the `Pipeline` stops automatically after iterating beyond the last `PipelineComponent` in its list of operations; if `True`, the execution loops back into the first component

#### Running a Pipeline as decorator
A `Pipeline` can be used to generate kwargs for a function (i.e., based on the content of the persistent data-object).
This requires the data-object being unpackable like a mapping (e.g. a dictionary).
```
>>> @Pipeline(...).run_for_kwargs(...)
... def function(arg1, arg2): ...
```
Arguments that are passed to a call of the decorated function take priority over those generated by the `Pipeline.run`.
