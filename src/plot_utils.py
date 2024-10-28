from typing import Callable, Any, Optional
import matplotlib.pyplot as plt
from got import Got, Response
from dataclasses import dataclass, replace
import utils


@dataclass
class LogFile:
    path: str
    kwargs: Optional[dict[str, Any]] = None


@dataclass
class Roller:
    name: str
    fn: Callable[[list[Response]], Any]
    rate: bool = False
    kwargs: Optional[dict[str, Any]] = None


@dataclass
class Fig:
    title: str
    x: str
    y: str


def fig(figs: list[Fig], subplots: Optional[tuple[int, int]] = None):
    if subplots is not None:
        fig, axes = plt.subplots(*subplots)
    else:
        fig, ax = plt.subplots()
        axes = [ax]

    fig.set_size_inches(15, 8)

    for f, ax in zip(figs, axes):
        ax.set_title(f.title)
        ax.set_xlabel(f.x)
        ax.set_ylabel(f.y)
    if subplots is not None:
        return fig, axes
    else:
        return fig, axes[0]


def rolling(
    ax,
    got: Got,
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units='s',
    **kwargs,
):
    for roller in rollers:
        times, y = got.rolling(
            rate=roller.rate,
            window=window_secs,
            fn=roller.fn,
            zeroed_times=zeroed_times,
            const_stride_secs=const_stride_secs,
        )
        times = utils.time_units_transform(times_units, times)
        if roller.kwargs is not None:
            merged = {**kwargs, **roller.kwargs}
        else:
            merged = kwargs
        ax.plot(times, y, label=roller.name, **merged)


def overlay(
    ax,
    log_files: dict[str, LogFile],
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units='s',
):
    for id, lf in log_files.items():
        got = Got(lf.path)
        _rollers = [replace(roller, name=f'{id}: {roller.name}') for roller in rollers]
        if lf.kwargs is not None:
            rolling(
                ax,
                got,
                _rollers,
                window_secs,
                zeroed_times,
                const_stride_secs,
                times_units,
                **lf.kwargs,
            )
        else:
            rolling(
                ax,
                got,
                _rollers,
                window_secs,
                zeroed_times,
                const_stride_secs,
                times_units,
            )
