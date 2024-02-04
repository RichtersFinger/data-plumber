![Tests](https://github.com/RichtersFinger/data-plumber/actions/workflows/tests.yml/badge.svg?branch=main)

# data-plumber
`data-plumber` is a lightweight but versatile python-framework for multi-stage
information processing. It allows to construct processing pipelines from both
atomic building blocks and via recombination of existing pipelines. Forks
enable more complex (i.e. non-linear) orders of execution. Pipelines can also
be collected into arrays that can be executed at once with the same input
data.

## Contents
1. [Minimal Exampe](#minimal-usage-example)
1. [Install](#install)
1. [Documentation](#documentation)
1. [Changelog](CHANGELOG.md)

## Minimal usage example
Consider a scenario where the contents of a dictionary have to be validated
and a suitable error message has to be generated. Specifically, a valid input-
dictionary is expected to have a key "data" with the respective value being
a list of integer numbers. A suitable pipeline might look like this
```
>>> from data_plumber import Stage, Pipeline, Previous
>>> pipeline = Pipeline(
        Stage(
            primer=lambda **kwargs: "data" in kwargs,
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "" if primer else "missing key"
        ),
        Stage(
            requires={Previous: 0},
            primer=lambda data, **kwargs: isinstance(data, list),
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "" if primer else "bad type"
        ),
        Stage(
            requires={Previous: 0},
            primer=lambda data, **kwargs: all(isinstance(i, int) for i in data),
            status=lambda primer, **kwargs: 0 if primer else 1,
            message=lambda primer, **kwargs: "validation success" if primer else "bad type in data"
        ),
        exit_on_status=1
    )
>>> pipeline.run(**{}).stages
[('missing key', 1)]
>>> pipeline.run(**{"data": 1}).stages
[('', 0), ('bad type', 1)]
>>> pipeline.run(**{"data": [1, "2", 3]}).stages
[('', 0), ('', 0), ('bad type in data', 1)]
>>> pipeline.run(**{"data": [1, 2, 3]}).stages
[('', 0), ('', 0), ('validation success', 0)]
```

## Install
Install using `pip` with
```
pip install data-plumber
```
Consider installing in a virtual environment.

## Documentation

* [Stage](docs/stage.md)
* [Pipeline](docs/pipeline.md)
