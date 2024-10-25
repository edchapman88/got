from typing import Callable, Any
import utils


class Response:
    def __init__(self, recv: int, success: bool):
        # response receive time in ns.
        self.recv = recv
        self.success = success

    @staticmethod
    def parse(line: str):
        [time, info] = line.split(maxsplit=1, sep=" ")
        time = int(time.replace("[", "").replace("]", ""))

        success = bool(int(info[0]))
        return Response(time, success)


class Got:
    def __init__(self, log_file_pth: str):
        with open(log_file_pth) as f:
            lines = f.readlines()
        self._lines = lines
        self.responses = list(map(Response.parse, lines))

    def __len__(self):
        return len(self.responses)

    def times_ns(self, zeroed=False) -> list[int]:
        times = list(map(lambda x: x.recv, self.responses))
        if zeroed:
            return self._zero_translation(times)
        return times

    def times_s(self, zeroed=False) -> list[float]:
        times = utils.time_units_transform("s", self.times_ns(zeroed=False))
        if zeroed:
            return self._zero_translation(times)
        return times

    @staticmethod
    def _zero_translation(values):
        return list(map(lambda x: x - min(values), values))

    def rolling(
        self,
        window: float,
        fn: Callable[[list[Response]], Any],
        rate=False,
        const_stride_secs=-1.0,
        zeroed_times=False,
    ) -> tuple[list[int], list[Any]]:
        """
        Evaluate the function on a rolling window.
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
        times = self.times_ns()
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
                    win = self.responses[trail:lead_exclusive]
                    calc(win)

            case _ if const_stride_secs == -1.0:
                for lead_inclusive, t in enumerate(times):
                    # increment the trailing edge of the window while the window is too large
                    while (t - times[trail]) > win_ns:
                        trail += 1
                    win = self.responses[trail : lead_inclusive + 1]
                    calc(win)
                win_leading_times = times
            case _:
                raise Exception("Invalid value for const_stride_steps")

        if zeroed_times:
            return (self._zero_translation(win_leading_times), calc_results)
        else:
            return (win_leading_times, calc_results)

    def success(self) -> list[bool]:
        return list(map(lambda x: x.success, self.responses))

    def num_ok(self) -> int:
        return self.success().count(True)

    def num_err(self) -> int:
        return self.success().count(False)
