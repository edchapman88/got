from typing import Callable, Any, Optional
import matplotlib.pyplot as plt
from got import Got, Response
from eyes import Eyes, Cpu, Mem, Disk, Nginx, Netflow
from dataclasses import dataclass, replace
import utils
from enum import Enum, auto


class LogFileType(Enum):
    """Either a 'got' log file created by the 'getting' HTTP load generator, or a 'telegraf' log file created by the telegraf system metrics pipeline."""

    GOT = auto()
    TELEGRAF = auto()


@dataclass
class LogFile:
    """The path to a log file, and matplotlib kwargs to be applied when plotting this data."""

    log_type: LogFileType
    path: str
    kwargs: Optional[dict[str, Any]] = None


@dataclass
class Roller:
    """A function callable on a window of data (list[Any]), with associated meta-data. kwargs are passed on to matplotlib when plotting a rolling window with this Roller."""

    name: str
    fn: Callable[[list[Any]], Any]
    rate: bool = False
    kwargs: Optional[dict[str, Any]] = None


@dataclass
class Fig:
    title: str
    x: str
    y: str


def fig(figs: list[Fig], subplots: Optional[tuple[int, int]] = None):
    """Convenience function to create an anotated matplotlib figure with one or many subplots."""

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


def plot_got_rollers(
    ax,
    path: str,
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units='s',
    **kwargs,
):
    got = Got(path)
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


def plot_telegraf_rollers(
    ax,
    path: str,
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units='s',
    **kwargs,
):
    # telegraf will be dict[str, list[str | dict[str,Any]]]
    streams = kwargs.pop('telegraf')
    with open(path, 'r') as f:
        eyes = Eyes(f.readlines())
    for stream_id, stream in streams.items():
        # a stream_id is e.g. 'cpu', and the stream is a list of fields, e.g ['usage_system', {'usage_user': plotting_kw}]
        for field in stream:
            if isinstance(field, str):
                kw = {}
            else:
                field = field.key()
                kw = field.value()
            # telegraf timestamps are in seconds, convert to nano-seconds as expected by `rolling`
            times = list(map(lambda x: int(1e9 * x.timestamp), eyes[stream_id]))
            values = list(map(lambda x: x[field], eyes[stream_id]))
            # apply rolling window
            for roller in rollers:
                window_end_times, rolling_vals = utils.rolling(
                    times,
                    values,
                    window=window_secs,
                    fn=roller.fn,
                    rate=roller.rate,
                    const_stride_secs=const_stride_secs,
                    zeroed_times=zeroed_times,
                )
                window_end_times = utils.time_units_transform(
                    times_units, window_end_times
                )
                if roller.kwargs is not None:
                    merged = {**kw, **roller.kwargs}
                else:
                    merged = kwargs
                ax.plot(
                    window_end_times,
                    rolling_vals,
                    label=f'{roller.name} {stream_id} {field}',
                    **merged,
                )


def overlay_rolling(
    ax,
    log_files: dict,
    rollers: list[Roller],
    window_secs: float,
    zeroed_times=False,
    const_stride_secs=-1.0,
    times_units='s',
):
    """Plot a set of rolling window data series onto an existing axis by specifying the log files containing the data, and the Roller functions to evaulate over each window."""

    for id, lf in log_files.items():
        _rollers = [replace(roller, name=f'{id}: {roller.name}') for roller in rollers]
        kwargs = {}
        if lf.kwargs is not None:
            kwargs = lf.kwargs

        match lf.log_type:
            case LogFileType.GOT:
                plot_got_rollers(
                    ax,
                    lf.path,
                    _rollers,
                    window_secs,
                    zeroed_times,
                    const_stride_secs,
                    times_units,
                    **kwargs,
                )
            case LogFileType.TELEGRAF:
                plot_telegraf_rollers(
                    ax,
                    lf.path,
                    _rollers,
                    window_secs,
                    zeroed_times,
                    const_stride_secs,
                    times_units,
                    **kwargs,
                )
            case u:
                raise Exception(f'LogFileType: {u} is unimplemented')


def show_combined_legends(axes: list[Any], **kwargs):
    lines = []
    [lines.extend(ax.get_lines()) for ax in axes]
    axes[0].legend(handles=lines, **kwargs)
