from typing import Any, Callable


def time_units_transform(unit: str, times_ns: list[int]):
    """Transform a list of times in nano-seconds into the desired units."""

    match unit:
        case 's':
            return list(map(lambda x: x / 1_000_000_000, times_ns))
        case _:
            raise Exception(f'time unit transform for unit: {unit} unimplemented')


def zero_translation(values):
    return list(map(lambda x: x - min(values), values))


def rolling(
    times: list[int],
    values: list[Any],
    window: float,
    fn: Callable[[list[Any]], Any],
    rate=False,
    const_stride_secs=-1.0,
    zeroed_times=False,
) -> tuple[list[int], list[Any]]:
    """
    Evaluate the function on a rolling window.
    `times` is the list of timestamps (nano-seconds since the Unix epoch) at which the `values` occured.
    `values` is the list of data over which the rolling window will be evaluated.
    `window` is measured in seconds.
    `rate` normalises the value returned by the function by the window length (in seconds) to create a rate with units 's^(-1)'. `False` by default.
    `const_stride_secs` sets the window stride to a constant value (seconds), rather that evaluating a window at each data point (variable stride). `-1.0` by default, which uses variable stride.
    `zeroed_times` subtracts `min(times)` from all times to translate the time axis to start at `0.0`. `False` by default, which allows 'syncing' data that was captured by multiple observers.
    Returns a tuple containing 1. a list containing the end-time of every window (ns), and 2. a list containing the values return from `fn` for each window.
    """
    win_ns = window * 1_000_000_000
    const_stride_secs_ns = int(round(const_stride_secs * 1_000_000_000))
    # Cursor for trailing edge of the window.
    trail = 0
    win_leading_times = []
    calc_results = []

    def calc(win):
        if rate:
            calc_results.append(fn(win) / window)
        else:
            calc_results.append(fn(win))

    match const_stride_secs:
        case _ if const_stride_secs > 0.0:
            # Cursor for the leading edge of the window, but to be excluded from the window.
            lead_exclusive = 0
            for t in range(
                times[0] + const_stride_secs_ns, times[-1], const_stride_secs_ns
            ):
                win_leading_times.append(t)
                # seek leading cursor
                while times[lead_exclusive] <= t:
                    lead_exclusive += 1
                # seek trailing cursor
                while (t - times[trail]) > win_ns:
                    trail += 1
                win = values[trail:lead_exclusive]
                calc(win)

        case _ if const_stride_secs == -1.0:
            for lead_inclusive, t in enumerate(times):
                # increment the trailing edge of the window while the window is too large
                while (t - times[trail]) > win_ns:
                    trail += 1
                win = values[trail : lead_inclusive + 1]
                calc(win)
            win_leading_times = times
        case _:
            raise Exception('Invalid value for const_stride_steps')

    if zeroed_times:
        return (zero_translation(win_leading_times), calc_results)
    else:
        return (win_leading_times, calc_results)
