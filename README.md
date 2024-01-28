# pypelines
lightweight but versatile python-framework for multi-stage information processing

## design/(prevision) usage samples

### concept

```
Pipeline(
    Stage(
        requires: None
        primer: lambda in_, **kwargs: "key" in in_
        action: ...
        message: lambda primer, **kwargs: "missing key" if primer else ""
        status: lambda primer, **kwargs: 0 if primer else 1
    ),
    Stage(
        requires: {Previous: 0}
        primer: lambda in_, **kwargs: isinstance(in_["key"], list)
        action: ...
        message: ...
        status: ...
    ),
    ...,
    Stage(
        requires: {Previous: (lambda status: status != 1)}
        primer: lambda in_, **kwargs: <last stage for valid input>
        action: lambda in_, out, **kwargs: out.update({"key": in_["key]})
        message: ...
        status: lambda primer, **kwargs: 2 if primer else 1  # exit by using status=2
    ),
    Stage(  # default value
        requires: {First: 1}
        primer: ...
        action: lambda out, **kwargs: out.update({"key": <default value>})
        message: ...
        status: ...
    ),
    exit_on_status=2,
    loop=False,
    ...
)
```


### classes
```
class Stage:
    process: Callable[[PipelineData], PipelineData]
    response: Callable[[PipelineData], int]
    requires: dict[Stage, int]  # Stage->uuid4
    uuid4: 
    ...
class Fitting:
    ...
class Pipeline:
    ...
class Pipearray:
    ...
class PipelineOutput:
    stages: list[tuple[str, int]]  # Stage->uuid4
    request: dict[str, Any]  # kwargs of pipeline.run
    data: Any
    ...
```


### assemble at once
```
stage_a = Stage(...)
...
pipeline = Pipeline(
    stage_a, stage_b, stage_c, ...
)
```

### assemble piece-wise
```
stage_a = Stage(...)
...
pipeline = Pipeline(
    stage_b, ...
)
pipeline.prepend(stage_a)
pipeline.append(stage_c)
```

### concat?
```
stage_a = Stage(...)
...
pipeline = stage_a + stage_b + ...  # type: Pipeline
```

### re-usable segments
```
segment_a = Pipeline(...)
segment_b = Pipeline(...)
...
pipeline = Pipeline(
    *segment_a, *segment_b, ...,
)
```

### control flow/fittings
conditional
```
stage_a = Stage(...)
stage_b = Stage(...)
stage_c = Stage(...)
fitting = Fitting(stage_b, stage_c)
..
pipeline = Pipeline(
    stage_a, fitting,
)
```
loop/jump? (requires named stages/segments)
```
stage_a = Stage(...)
stage_b = Stage(...)
stage_c = Stage(...)
bypass = Fitting("b")
..
pipeline = Pipeline(
    "a", "b", "c", "l",
    a=stage_a, b=stage_b, c=stage_c, l=bypass
)
```

### trigger/run
```
pipeline = Pipeline(...)
result = pipeline.run(data)
result2 = pipeline.run(data2)
```

### chain
```
pipeline1 = Pipeline(...)
pipeline2 = Pipeline(...)
result = pipeline1.run(pipeline2.run(data))
result2 = Pipeline(pipeline1, pipeline2, ...).run(data)
# result == result2
```

### vectorize (threaded)
```
pipeline1 = Pipeline(...)
pipeline2 = Pipeline(...)
pipearray = Pipearray(pipeline1, pipeline2)
```
