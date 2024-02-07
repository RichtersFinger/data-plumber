### PipelineOutput

[Documentation](../README.md#documentation)

#### List of properties
The output of a `Pipeline.run` is an object of type `PipelineOutput`.
This object has the following properties:
* **records**: a list of `StageRecord`s corresponding to all `Stage`s executed by the `Pipeline`; `StageRecord`s themselves are a collection of properties
  * `index`: index position in `Pipeline`'s sequence of `PipelineComponents`
  * `id_`: name/id of `Stage`
  * `message`: the message returned by the `Stage`
  * `status`: the message returned by the `Stage`

  *(for legacy support (<=1.11.) this property can also be indexed, where `message` and `status` are returned for indices 0 and 1, respectively)*
* **kwargs**: a dictionary with the keyword arguments used in the `Pipeline.run`
* **data**: the persistent data-object that has been processed through the `Pipeline`

For convenience, the last `StageRecord` generated in the `Pipeline` can be investigated using the shortcuts
* **last_record**: `StageRecord` of last component that generated an output
* **last_status**: status-part of the `last_record`
* **last_message**: message-part of the `last_record`
