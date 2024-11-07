from typing import Callable, Any
import utils


class Response:
    def __init__(self, recv: int, success: bool):
        # response receive time in ns.
        self.recv = recv
        self.success = success

    @staticmethod
    def parse(line: str):
        [time, info] = line.split(maxsplit=1, sep=' ')
        time = int(time.replace('[', '').replace(']', ''))

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
            return utils.zero_translation(times)
        return times

    def times_s(self, zeroed=False) -> list[float]:
        times = utils.time_units_transform('s', self.times_ns(zeroed=False))
        if zeroed:
            return utils.zero_translation(times)
        return times

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
        times = self.times_ns()
        values = self.responses

        return utils.rolling(
            times, values, window, fn, rate, const_stride_secs, zeroed_times
        )

    def success(self) -> list[bool]:
        return list(map(lambda x: x.success, self.responses))

    def num_ok(self) -> int:
        return self.success().count(True)

    def num_err(self) -> int:
        return self.success().count(False)
