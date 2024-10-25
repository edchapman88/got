from got import Response


def count_err(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(False)
    return float(count)


def count_ok(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(True)
    return float(count)


def proportion_ok(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(True)
    return float(count) / float(len(window))


def time_units_transform(unit: str, times_ns: list[int]):
    match unit:
        case "s":
            return list(map(lambda x: x / 1_000_000_000, times_ns))
        case _:
            raise Exception(f"time unit transform for unit: {unit} unimplemented")
