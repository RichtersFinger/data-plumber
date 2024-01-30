# pypelines
`pypelines` is a lightweight but versatile python-framework for multi-stage
information processing. It allows to construct processing pipelines from both
atomic building blocks and via recombination of existing pipelines. Forks
enable more complex (i.e. non-linear) orders of execution. Pipelines can also
be collected into arrays that can be executed at once with the same input
data.

## Minimal usage example
Consider a scenario where the contents of a dictionary have to be validated
and a suitable error message has to be generated. Specifically, a valid input-
dictionary is expected to have a key "list" with the respective value being
a list of integer numbers. A suitable pipeline might look like this
```
>>> from pypelines import Stage, Pipeline, Previous
>>> pipeline = Pipeline(
        Stage(
            primer=lambda in_, **kwargs: "list" in in_,
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "" if primer else "missing key"
        ),
        Stage(
            requires={Previous: 0},
            primer=lambda in_, **kwargs: isinstance(in_["list"], list),
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "" if primer else "bad type"
        ),
        Stage(
            requires={Previous: 0},
            primer=lambda in_, **kwargs: all(isinstance(i, int) for i in in_["list"]),
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "validation success" if primer else "bad type in list"
        ),
        exit_on_status=1
    )
>>> pipeline.run(**{}).stages
[('missing key', 1)]
>>> pipeline.run(**{"list": 1}).stages
[('', 0), ('bad type', 1)]
>>> pipeline.run(**{"list": [1, 2, 3]}).stages
[('', 0), ('', 0), ('validation success', 0)]
```
