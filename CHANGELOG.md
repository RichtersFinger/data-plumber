# Changelog

## [1.14.0] - 2024-03-30

### Added

- added `finalize_output`-override option to `Pipeline.run` (`e951f97`)

## [1.13.0] - 2024-03-23

### Changed

- `Pipeline` now supports empty `PipelineComponent`s as labels within pipeline (`631bc3d`)

## [1.12.1] - 2024-02-07

### Fixed

- update and fix errors in documentation (`2318210`)

## [1.12.0] - 2024-02-05

### Changed

- added a list of previous `StageRecord`s as kwarg for the call to a `Fork`'s conditional (`2f1cb77`)
- changed `StageRecord` into a proper dataclass (`e7eae6d`)

## [1.11.0] - 2024-02-04

### Changed

- added common base class `_PipelineComponent` for `Pipeline` components `Stage` and `Fork` (`f628159`)

### Added

- added docs to package metadata (`061e311`)
- names for `PipelineComponents` can now be declared in extension methods (`append`, `prepend`, ...) (`8363284`)
- `Pipeline` now supports `in`-operator (usable with either component directly or its name/id) (`5701073`)
- added requirements for `Pipeline` to be unpacked as mapping (`b2db8fa`)

### Fixed

- fixed issue where `Fork`-objects were internally not registered by their id (`b267ca4`)

## [1.8.0] - 2024-02-03

### Changed

- refactored `Fork` and `Stage` to transform string/integer-references to `Stage`s into `StageRef`s (`7ba677b`)

### Added

- added decorator-factory `Pipeline.run_for_kwargs` to generate kwargs for function calls (`fe616b2`)
- added optional `Stage`-callable to export kwargs into `Pipeline.run` (`8eca1bc`)
- added even more types of `StageRef`s: `PreviousN`, `NextN` (`576820c`)
- added `py.typed`-marker to package (`04a2e1d`)
- added more types of `StageRef`s: `StageById`, `StageByIndex`, `StageByIncrement` (`92d57ad`)

## [1.4.0] - 2024-02-01

### Changed

- refactored internal modules (`cf7045f`)

### Added

- added `StageRefs` `Next`, `Last`, and `Skip` (`14abaa7`)
- added optional finalizer-`Callable` to `Pipeline` (`d95e5b6`)
- added support for `Callable` in `Pipeline`-argument `exit_on_status` (`154c67b`)

### Fixed

- `PipelineOutput.last_X`-methods now return `None` in case of empty records (`b7a6ba1`)

## [1.0.0] - 2024-01-31

### Changed

- **Breaking:** refactor `PipelineOutput` and related types (`1436ca1`)
- **Breaking:** replaced forwarding kwargs of `Pipeline.run` as dictionary `in_` into `Stage`/`Fork`-`Callable`s by forwarding directly (`f2710fa`, `b569bb9`)

### Added

- added missing information in module- and class-docstrings (`7896742`)

## [0.1.0] - 2024-01-31

initial release
