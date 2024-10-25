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


def fig(title: str, x: str, y: str):
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 8)
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig, ax


def rolling(
    ax,
    got: Got,
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units="s",
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
        ax.plot(times, y, label=roller.name)


def overlay(
    ax,
    log_files: dict[str, LogFile],
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units="s",
):
    for id, lf in log_files.items():
        got = Got(lf.path)
        _rollers = [replace(roller, name=f"{id}: {roller.name}") for roller in rollers]
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
