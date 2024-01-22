# pypelines
lightweight but versatile python-framework for multi-stage information processing

## design/(prevision) usage samples

### classes
```
class Stage:
    process: Callable[[PipelineData], PipelineData]
    response: Callable[[PipelineData], int]
    requires: dict[Stage, int]  # Stage->uuid4
    ...
class Fitting:
    ...
class Pipeline:
    ...
class Pipearray:
    ...
class PipelineData:
    stages: dict[Stage, int]  # Stage->uuid4
    data: Any
    in: Any
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
    segment_a, segment_b, ...,
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

### trigger
```
pipeline = Pipeline(...)
result = pipeline.trigger(data)
result2 = pipeline.trigger(data2)
```

### chain
```
pipeline1 = Pipeline(...)
pipeline2 = Pipeline(...)
result = pipeline1.trigger(pipeline2.trigger(data))
result2 = Pipeline(pipeline1, pipeline2, ...).trigger(data)
# result == result2
```

### vectorize (threaded)
```
pipeline1 = Pipeline(...)
pipeline2 = Pipeline(...)
pipearray = Pipearray(pipeline1, pipeline2)
```
