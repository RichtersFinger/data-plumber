### Examples

[Documentation](../README.md#documentation)

#### Input Processing Revisited
Reconsider the introductory example of validating dictionary content.
The described scenario where data is validated against some schema with increasing attention to detail with every `Stage` and generating helpful response messages is common in the context of, for example, user input.

The following section goes into more detail regarding the reasoning for the example-`Pipeline`'s setup.
A `Pipeline` generally iterates the provided sequence of `Stage`s if there is no flow control included (like in this example).
Within a `Stage` there is again an order of operations for the `Callable`s as defined in the constructor (`primer` > `action` > `export` > `status` > `message`).
Starting with the first `Stage` of the example,
```
    ...
...   Stage(  # validate "data" is passed into run
...     primer=lambda **kwargs: "data" in kwargs,
...     status=lambda primer, **kwargs: 0 if primer else 1,
...     message=lambda primer, **kwargs: "" if primer else "missing argument"
...   ),
    ...
```
the `primer` is executed first.
This function validates that an argument with keyword `data` has been passed in to the `Pipeline.run`, i.e. `Pipeline.run(data=...)`.
Following this evaluation, the result can be used in the next two `Callable`s, `status` and `message` to generate an output from this `Stage` with appropriate properties for the given situation.

In the next `Stage`,
```
    ...
...   Stage(  # validate "data" is list
...     requires={Previous: 0},
...     primer=lambda data, **kwargs: isinstance(data, list),
...     status=lambda primer, **kwargs: 0 if primer else 1,
...     message=lambda primer, **kwargs: "" if primer else "bad type"
...   ),
    ...
```
the general structure is similar.
A `primer` is executed to validate a property of the `data`-keyword argument. This keyword can now be written explicitly into the `lambda`'s signature (instead of covering this argument implicitly with `**kwargs` like before) since this call to `primer` precedes a requirement-check.
The requirement given here declares only a single requirement, i.e. the previous `Stage` (denoted by the `StageRef` named `Previous`) returned with a status of 0.
Consequently, this second `Stage` is only executed if the `primer` of the first `Stage` returned a value of `True`.

The third `Stage` is conceptually the same as the second one but intended to handle another aspect of the validation.

The exit from the `Pipeline.run` can occur either after completing the third `Stage` or if a `Stage` returns a specific status as defined by the kwarg of the Pipeline itself:
```
>>> pipeline = Pipeline(
...  ...
...   exit_on_status=1
... )
```
This is the reason for returning a status of 1 in all `Stage`s if any stage of the validation fails.

In the following, two additional features of `data-plumber` are demonstrated by extending the original example.

#### Input Processing - Formatting Output Data
A `Pipeline` can also handle reformatting of input data into a desired format.
Suppose that, following validation, only the sum of all integers given in the list `data` is of interest.
In order make this information readily available right after execution within the `PipelineOutput`-object that is returned by a `Pipeline.run`, one may add a suitable `action` callable in the last `Stage` of the previous setup:
```
    ...
...   Stage(  # validate "data" contains only int
...    ...
...     action=lambda data, primer, **kwargs:
...       data.update{"sum": sum(data)} if primer else None
...    ...
...   ),
    ...
```
With this change, after full validation, a key `sum` is added to the dictionary in `PipelineOutput.data`, i.e.
```
>>> output = pipeline.run(data=[1, 2, 3])
>>> output.data["sum"]
6
```

#### Input Processing - Optional Values
Consider that the data that is fed into the `Pipeline.run`-command is an optional property.
Consequently, it is fine if it is missing but, if it exists, it should satisfy a specific format.

This scenario can, for example, be realized using a `Fork`.
A `Fork` takes a single `Callable` on construction which returns a reference to another `Stage` as next target in the current `Pipeline.run` or give an exit-signal (by returning `None`).
Here, the latter is more interesting.
We can change the initial portion of the `Pipeline` setup to accomodate for the changes in validation logic:
```
>>> from data_plumber import Next
>>> pipeline = Pipeline(
...   Fork(
...     lambda **kwargs: Next if "data" in kwargs else None
...   )
...   Stage(  # validate "data" is list
...     ...
...   ),
...  ...
...   exit_on_status=1
... )
```
Now, the validation of the first `Stage` in the initial example is replaced with a `Fork`.
`Next` is another pre-defined `StageRef` pointing at the next `PipelineComponent` in the `Pipeline`'s sequence.

Note that for this setup, if `data` is missing, the returned `PipelineOutput` does not contain any `StageRecord`s as `Fork` does not output any status.
In order to have both, the `Fork`-logic and a `StageRecord`, the `Fork` has to be the second component.
Using the `stages`-kwarg for the `Fork`'s `Callable` enables to use the status from a previous `Stage` and circumvent a duplicate validation.
