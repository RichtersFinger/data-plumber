"""
# data_plumber/pipeline.py

The `pipeline`-module defines the `Pipeline`-class as the core-component
of the data-plumber-framework.
"""

from typing import Optional, Callable, Any, Iterator
from functools import wraps
from uuid import uuid4

from .component import _PipelineComponent
from .context import PipelineContext
from .error import PipelineError
from .output import _StageRecord, PipelineOutput
from .fork import Fork
from .stage import Stage


class Pipeline:
    """
    A `Pipeline` provides the core-functionality of the `data-plumber`-
    framework. `Pipeline`s can be defined either with (explicitly) named
    `_PipelineComponent`s (`Stage` or `Fork`) or immediately by
    providing `_PipelineComponent`s as positional arguments.

    Example usage:
     >>> from data_plumber import Pipeline, Stage, Fork
     >>> Pipeline(
             Stage(...),
             Stage(...),
             Fork(...)
         )
     <data_plumber.pipeline.Pipeline object at ...>
     >>> Pipeline(
             Stage(...),
             Stage(...),
             Fork(...)
         ).run(...)
     <data_plumber.output.PipelineOutput object at ...>

    Keyword arguments:
    args -- positional `_PipelineComponent`s referenced by id or
            explicit as objects
    kwargs -- assignment of custom identifiers for `_PipelineComponent`s
              used in the positional section
    initialize_output -- generator for initial data of `Pipeline.run`s
                         (default lambda: {})
    finalize_output -- `Callable` that is executed after the execution
                       of `Pipeline.run` exits; gets passed the
                       `Pipeline`'s persistent `data`-object and `run`'s
                       kwargs (see also docs of individual
                       `_PipelineComponent`s)
                       (default None)
    exit_on_status -- stop `Pipeline` execution if
                      * any `Stage` returns this status (int)
                      * it returns `True` (Callable)
                      (default `None`)
    loop -- if `True`, loop around and re-iterate `_PipelineComponent`s
            after completion of last `_PipelineComponent` in `Pipeline`
            (default `False`)
    """
    def __init__(
        self,
        *args: str | _PipelineComponent,
        initialize_output: Callable[..., Any] = lambda: {},
        finalize_output: Optional[Callable[..., Any]] = None,
        exit_on_status: Optional[int | Callable[[int], bool]] = None,
        loop: bool = False,
        **kwargs: _PipelineComponent
    ) -> None:
        self._initialize_output = initialize_output
        self._finalize_output = finalize_output
        self._exit_on_status = \
            exit_on_status if callable(exit_on_status) \
            else lambda status: status == exit_on_status
        self._loop = loop
        self._id = str(uuid4())

        # dictionary of PipelineComponents by their given name/id
        self._stage_catalog: dict[str, _PipelineComponent] = {}
        self._update_catalog(*args, **kwargs)

        # build actual pipeline with references to PipelineComponents
        # from self._stage_catalog
        self._pipeline = list(map(str, args))

    def _update_catalog(self, *args, **kwargs):
        self._stage_catalog.update(kwargs)
        for s in args:
            if isinstance(s, str):
                continue
            self._stage_catalog.update({str(s): s})

    def _meets_requirements(self, _s: str, context: PipelineContext) -> bool:
        s = self._stage_catalog[_s]
        assert isinstance(s, Stage)
        if s.requires is None:
            return True
        for ref, req in s.requires.items():
            # get target Stage from StageRef
            ref_output = ref.get(
                context
            )
            # get latest status of that Stage
            match_status = next(
                (stage.status for stage in reversed(context.records)
                    if stage.id_ == ref_output.stage),
                None
            )
            if match_status is None:
                # this Stage does not exist or has not been executed
                raise PipelineError(
                    f"Referenced Stage '{ref_output.stage}' (required by Stage"
                    + f" '{_s}') has not been executed yet. "
                    + f"Records until error: {context.records}"
                )
            if callable(req):
                if not req(status=match_status):  # type: ignore[call-arg]
                    # requirement not met
                    return False
            else:
                if match_status != req:
                    # requirement not met
                    return False
        return True

    def _loop_index(self, index: int) -> int:
        if self._loop:  # loop by truncating index
            return index % len(self._pipeline)
        return index

    def _validate_external_kwargs(self, **kwargs):
        reserved_words = ["out", "primer", "status", "count"]
        # check for reserved kwargs
        if (bad_kwarg := next(
            (p for p in kwargs if p in reserved_words),
            None
        )):
            raise PipelineError(
                f"Keyword '{bad_kwarg}' is reserved in the context of a "
                + f"'Pipeline.run'-command. (Reserved words: {reserved_words})"
            )

    @property
    def id(self) -> str:
        """Returns a `Pipeline`'s `id`."""
        return self._id

    @property
    def catalog(self) -> dict[str, _PipelineComponent]:
        """
        Returns a (shallow) copy of the `Pipeline`'s
        `_PipelineComponent`-catalog.
        """
        return self._stage_catalog.copy()

    @property
    def stages(self) -> list[str]:
        """
        Returns a copy of the `Pipeline`'s list of
        `_PipelineComponent`s.
        """
        return self._pipeline.copy()

    def run(self, **kwargs) -> PipelineOutput:
        """
        Trigger `Pipeline` execution.

        Keyword arguments:
        kwargs -- keyword arguments that are forwarded into
                  `_PipelineComponent`s
        """

        self._validate_external_kwargs(**kwargs)

        records: list[_StageRecord] = []  # record of results
        data = self._initialize_output()  # output data

        stage_count = -1
        index = 0
        while True:
            index = self._loop_index(index)
            if index >= len(self._pipeline):  # detect exit point
                break

            _s = self._pipeline[index]
            try:
                s = self._stage_catalog[_s]
            except KeyError as exc:
                raise PipelineError(
                    f"Unable to resolve reference to Component id '{_s}' in Pipeline with " \
                    + f"stages {self._pipeline}. Records until error: {records}"
                ) from exc
            if isinstance(s, Fork):
                # ##########
                # Fork
                # get StageRef
                assert isinstance(s, Fork)
                stage_ref = s.eval(
                    PipelineContext(
                        self._pipeline, index, self._loop, records, kwargs,
                        data, stage_count
                    )
                )
                if stage_ref is None:  # exit pipeline on request
                    break
                # get target of StageRef
                ref = stage_ref.get(
                    PipelineContext(
                        self._pipeline, index, self._loop, records, kwargs,
                        data, stage_count
                    )
                )
                index = ref.index
                continue
            # ##########
            # Stage
            # requires
            assert isinstance(s, Stage)
            if not self._meets_requirements(
                _s, PipelineContext(
                    self._pipeline, index, self._loop, records, kwargs,
                    data, stage_count
                )
            ):
                index = index + 1
                continue
            # all requirements met
            stage_count = stage_count + 1
            # primer
            primer = s.primer(**kwargs, out=data, count=stage_count)
            # action
            s.action(
                **kwargs,
                out=data,
                primer=primer,
                count=stage_count
            )
            exported_kwargs = s.export(
                **kwargs,
                out=data,
                primer=primer,
                count=stage_count
            )
            self._validate_external_kwargs(**exported_kwargs)
            kwargs.update(exported_kwargs)
            # status/message
            status = s.status(
                **kwargs,
                out=data,
                primer=primer,
                count=stage_count
            )
            msg = s.message(
                **kwargs,
                out=data,
                primer=primer,
                count=stage_count,
                status=status
            )
            records.append(_StageRecord(index, _s, msg, status))
            if self._exit_on_status(status):
                break
            index = index + 1

        if self._finalize_output is not None:
            self._finalize_output(data=data, **kwargs)
        return PipelineOutput(
            [r.prune() for r in records],  # prune `_StageRecord`s
            kwargs,
            data
        )

    def run_for_kwargs(self, **kwargs):
        """
        Returns a decorator that can be used to generate kwargs for the
        decorated function based on the output of a `Pipeline.run`. This
        requires for the persistent data-object (`PipelineOutput.data`)
        to be a mapping that can be unpacked as `**PipelineOutput.data`.

        Using this decorator on a function and calling that function
         >>> @pipeline.run_for_kwargs(...)
             def f(...): ...
         >>> f()
        is equivalent to
         >>> f(**pipeline.run(...).data)

        Note that it is also possible to only generate a subset of all
        keyword arguments to a target function or have the target also
        require positional arguments (which then still have to be
        provided explicitly to the decorated function). When makign a
        call to the decorated function with kwargs that are also output
        from the `Pipeline.run`, the explicitly given arguments take
        priority.

        Keyword arguments:
        kwargs -- keyword arguments that are forwarded into
                  `Pipeline.run`
        """

        def decorator(function):
            @wraps(function)
            def wrapped(*args, **_kwargs):
                output = self.run(**kwargs)
                return function(*args, **(output.data | _kwargs))
            return wrapped
        return decorator

    def append(self, element: "str | _PipelineComponent | Pipeline") -> None:
        """Append `element` to the `Pipeline`."""
        if isinstance(element, Pipeline):
            self._update_catalog(**element.catalog)
            self._pipeline = self._pipeline + element.stages
            return
        self._update_catalog(element)
        self._pipeline.append(str(element))

    def prepend(self, element: "str | _PipelineComponent | Pipeline") -> None:
        """Prepend `element` to the `Pipeline`."""
        if isinstance(element, Pipeline):
            self._update_catalog(**element.catalog)
            self._pipeline = element.stages + self._pipeline
            return
        self._update_catalog(element)
        self._pipeline.insert(0, str(element))

    def insert(
        self,
        index: int,
        element: "str | _PipelineComponent | Pipeline"
    ) -> None:
        """Insert `element` into the `Pipeline` at `index`."""
        if isinstance(element, Pipeline):
            self._update_catalog(**element.catalog)
            self._pipeline = self._pipeline[:index] \
                + element.stages \
                + self._pipeline[index:]
            return
        self._update_catalog(element)
        self._pipeline.insert(index, str(element))

    def __add__(self, other):
        if not isinstance(other, _PipelineComponent) \
                and not isinstance(other, Pipeline):
            raise TypeError(
                "Incompatible type, expected '_PipelineComponent' or 'Pipeline'"
                    f" not '{type(other).__name__}'."
            )
        self.append(other)
        return self

    def __contains__(self, value):
        return \
            value in self._stage_catalog \
            or value in self._stage_catalog.values()

    def keys(self):
        return self._stage_catalog.keys()

    def __getitem__(self, key):
        return self._stage_catalog[key]

    def __iter__(self) -> Iterator[_PipelineComponent]:
        for s in self._pipeline:
            yield self._stage_catalog[s]

    def __len__(self):
        return len(self._pipeline)
