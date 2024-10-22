from typing import Callable, Any
import pandas as pd


class Response:
    def __init__(self, recv: float, success: bool):
        self.recv = recv
        self.success = success

    @staticmethod
    def parse(line: str):
        [time, info] = line.split(maxsplit=1, sep=" ")
        time = float(time.replace("[", "").replace("]", ""))

        success = bool(int(info[0]))
        return Response(time, success)


class Got:
    def __init__(self, log_file_pth: str):
        with open(log_file_pth) as f:
            lines = f.readlines()
        self._lines = lines
        self.responses = list(map(Response.parse, lines))
        self.df = pd.DataFrame({"time": self.times(), "success": self.success()})

    def __len__(self):
        return len(self.responses)

    def times(self, zeroed=True) -> list[float]:
        times = list(map(lambda x: x.recv, self.responses))
        if not zeroed:
            return times
        else:
            min_time = min(times)
            return list(map(lambda x: x - min_time, times))

    def rolling(
        self, window: float, fn: Callable[[list[Response]], Any]
    ) -> tuple[list[float], list[Any]]:
        """
        Evaluate the function on a rolling window.
        `window` is measured in seconds.
        Returns a tuple, `(start_times, calc_results)`, where `start_times` is a list containing the start time of every window (seconds), and `calc_results` is a list containing the values return from `fn` for each window.
        """
        win_ns = window * 1_000_000_000
        # cursors
        s = 0
        e = 0
        times = self.times()
        e_max = len(times) - 1
        start_times = []
        calc_results = []
        scanning = True
        while scanning:
            start_times.append(times[s] / 1_000_000_000)
            while times[e] - times[s] < win_ns:
                e += 1
                if e == e_max:
                    scanning = False
                    break
            win = self.responses[s:e]
            calc_results.append(fn(win))
            s += 1
        return (start_times, calc_results)

    def success(self) -> list[bool]:
        return list(map(lambda x: x.success, self.responses))

    def num_ok(self) -> int:
        return self.success().count(True)

    def num_err(self) -> int:
        return self.success().count(False)
