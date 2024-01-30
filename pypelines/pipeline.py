"""
# pypelines/pipeline.py

...
"""

from typing import Optional, Callable, Any, Iterator
from uuid import uuid4

from .context import StageRecord, PipelineContext, StageRef
from .error import PipelineError
from .output import PipelineOutput
from .fork import Fork
from .stage import Stage


class Pipeline:
    """
    A `Pipeline` provides the core-functionality of the pypelines-
    framework. `Pipeline`s can be defined either with (explicitly) named
    `Stage`s or immediately by providing `Stage`s as positional
    arguments.

    Keyword arguments:
    args -- positional `Stage`s/`Fork`s referenced by id or explicit as
            objects
    kwargs -- assignment of custom identifiers for `Stage`s/`Fork`s used
              in the positional section
    initialize_output -- generator for initial data of `Pipeline.run`s
                         (default lambda: {})
    exit_on_status -- stop `Pipeline` execution if any `Stage` returns
                      this status
                      (default `None`)
    loop -- if `True`, loop around and re-iterate `Stage`s after
            completion of last `Stage` in `Pipeline`
            (default `False`)
    """
    def __init__(
        self,
        *args: str | Stage | Fork,
        initialize_output: Callable[..., Any] = lambda: {},
        exit_on_status: Optional[int] = None,
        loop: bool = False,
        **kwargs: Stage | Fork
    ) -> None:
        self._initialize_output = initialize_output
        self._exit_on_status = exit_on_status
        self._loop = loop
        self._id = str(uuid4())

        # dictionary of Stages by Stage.id
        self._stage_catalog = {}
        self._update_catalog(*args, **kwargs)

        # build actual pipeline with references to Stages|Forks
        # from self._stage_catalog
        self._pipeline = list(map(str, args))

    def _update_catalog(self, *args, **kwargs):
        self._stage_catalog.update(kwargs)
        for s in args:
            if isinstance(s, str):
                continue
            self._stage_catalog.update({str(s): s})

    @property
    def id(self) -> str:
        """Returns a `Pipeline`'s `id`."""
        return self._id

    @property
    def catalog(self) -> dict[str, Stage]:
        """Returns a (shallow) copy of the `Pipeline`'s `Stage`-catalog."""
        return self._stage_catalog.copy()

    @property
    def stages(self) -> list[str]:
        """Returns a copy of the `Pipeline`'s list of `Stage`s."""
        return self._pipeline.copy()

    def run(self, **kwargs) -> PipelineOutput:
        """
        Trigger `Pipeline` execution.

        Keyword arguments:
        kwargs -- keyword arguments that are passed into `Stage`s as
                  dictionary `in_`
        """

        stages: list[StageRecord] = []  # record of results
        data = self._initialize_output()  # output data

        stage_count = -1
        index = 0
        while True:
            if self._loop:  # loop by truncating index
                index = index % len(self._pipeline)
            if index >= len(self._pipeline):  # detect exit point
                break

            _s = self._pipeline[index]
            try:
                s = self._stage_catalog[_s]
            except KeyError as exc:
                raise PipelineError(
                    f"Unable to resolve reference to Stage '{_s}' at stage #{str(stage_count)}. "
                    + f"Records until error: {', '.join(map(str, stages))}"
                ) from exc
            if isinstance(s, Fork):
                # ##########
                # Fork
                fork_target = s.eval(
                    PipelineContext(stages, kwargs, data, stage_count)
                )
                if fork_target is None:  # exit pipeline on request
                    break
                if isinstance(fork_target, StageRef):  # get id via StageRef.get
                    try:
                        fork_target = fork_target.get(
                            PipelineContext(stages, kwargs, data, stage_count)
                        )[0]
                    except TypeError as exc:
                        raise PipelineError(
                            f"Unable to resolve fork's StageRef '{str(fork_target)}' at stage #{str(stage_count)}. "
                            + f"Records until error: {', '.join(map(str, stages))}"
                        ) from exc
                try:
                    index = self._pipeline.index(fork_target)
                except ValueError as exc:
                    raise PipelineError(
                        f"Unable to resolve reference to '{str(fork_target)}' at stage #{str(stage_count)}. "
                        + f"Records until error: {', '.join(map(str, stages))}"
                    ) from exc
                continue
            # ##########
            # Stage
            # requires
            if s.requires is not None:
                req_met = True
                for ref, req in s.requires.items():
                    match = None
                    if isinstance(ref, str):  # by identifier
                        # find latest status of Stage with this identifier
                        match = next(
                            (stage for _, stage in enumerate(reversed(stages))
                                if stage[0] == ref),
                            default=None
                        )
                    else:  # by StageRef
                        match = ref.get(
                            PipelineContext(stages, kwargs, data, stage_count)
                        )
                    if match is None:
                        # this Stage has not been executed
                        raise PipelineError(
                            f"Referenced Stage '{str(ref)}' (required by Stage"
                            + f" '{_s}') has not been executed yet."
                        )
                    if callable(req):
                        if not req(status=match[2]):
                            # requirement not met
                            req_met = False
                            break
                    else:
                        if match[2] != req:
                            # requirement not met
                            req_met = False
                            break
                if not req_met:
                    index = index + 1
                    continue
            # all requirements met
            stage_count = stage_count + 1
            # primer
            primer = s.primer(in_=kwargs, out=data, count=stage_count)
            # action
            s.action(
                in_=kwargs,
                out=data,
                primer=primer,
                count=stage_count
            )
            # status/message
            status = s.status(
                in_=kwargs,
                out=data,
                primer=primer,
                count=stage_count
            )
            msg = s.message(
                in_=kwargs,
                out=data,
                primer=primer,
                count=stage_count,
                status=status
            )
            stages.append((_s, msg, status))
            if status == self._exit_on_status:
                break
            index = index + 1

        return PipelineOutput(
            list(map(lambda x: x[1:], stages)),  # trim StageRecord
            kwargs,
            data
        )

    def append(self, element: "str | Stage | Fork | Pipeline") -> None:
        """Append `element` to the `Pipeline`."""
        if isinstance(element, Pipeline):
            self._update_catalog(**element.catalog)
            self._pipeline = self._pipeline + element.stages
            return
        self._update_catalog(element)
        self._pipeline.append(str(element))

    def prepend(self, element: "str | Stage | Fork | Pipeline") -> None:
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
        element: "str | Stage | Fork | Pipeline"
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
        if not isinstance(other, Stage) and not isinstance(other, Pipeline):
            raise TypeError(
                "Incompatible type, expected 'Stage' or 'Pipeline' "
                    f"not '{type(other).__name__}'."
            )
        self.append(other)
        return self

    def __iter__(self) -> Iterator[Stage]:
        for s in self._pipeline:
            yield self._stage_catalog[s]

    def __len__(self):
        return len(self._pipeline)
