# Changelog

## [1.4.0] - 2024-02-01

### Changed

- refactored internal modules (`cf7045f`)

### Added

- added `StageRefs` `Next`, `Last`, and `Skip` (`14abaa7`)
- added optional finalizer-`Callable` to `Pipeline` (`d95e5b6`)
- added support for `Callable` in `Pipeline`-argument `exit_on_status` (`154c67b`)

### Fixed

- `PipelineOutput.last_X`-methods now return `None` in case of empty records (``)

## [1.0.0] - 2024-01-31

### Changed

- **Breaking:** refactor `PipelineOutput` and related types (`1436ca1`)
- **Breaking:** replaced forwarding kwargs of `Pipeline.run` as dictionary `in_` into `Stage`/`Fork`-`Callable`s by forwarding directly (`f2710fa`, `b569bb9`)

### Added

- added missing information in module- and class-docstrings (`7896742`)

## [0.1.0] - 2024-01-31

initial release
