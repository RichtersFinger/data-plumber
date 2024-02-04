### PipelineOutput

[Documentation](../README.md#documentation)

#### List of properties
The output of a `Pipeline.run` is an object of type `PipelineOutput`. This object has the following properties:
* **records**: a list of `StageRecord`s corresponding to all stages executed by the `Pipeline`; `StageRecord`s themselves are an Alias for a tuple of the message and status generated from the corresponding component
* **kwargs**: a dictionary with the keyword arguments used in the `Pipeline.run`
* **data**: the persistent data-object that has been processed through the `Pipeline`

For convenience, the last `StageRecord` generated in the `Pipeline` can be investigated using the conveniece-properties
* **last_record**: `StageRecord` of last component that generated an output
* **last_status**: status-part of the `last_record`
* **last_message**: message-part of the `last_record`
