from got import Response
from typing import Any

KLEENE_IP = '169.254.80.236'
HILBERT_IP = ''
MAC_IP = ''


def count_err(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(False)
    return float(count)


def count_ok(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(True)
    return float(count)


def proportion_ok(window: list[Response]) -> float:
    count = list(map(lambda x: x.success, window)).count(True)
    return float(count) / float(len(window))


def mean(window: list[Any]) -> float:
    return sum(window) / len(window)


def count_kleene_packets(window: list[Any]) -> int:
    return list(map(lambda x: x == KLEENE_IP, window)).count(True)


def count_hilbert_packets(window: list[Any]) -> int:
    return list(map(lambda x: x == HILBERT_IP, window)).count(True)


def count_mac_packets(window: list[Any]) -> int:
    return list(map(lambda x: x == MAC_IP, window)).count(True)


def time_units_transform(unit: str, times_ns: list[int]):
    match unit:
        case 's':
            return list(map(lambda x: x / 1_000_000_000, times_ns))
        case _:
            raise Exception(f'time unit transform for unit: {unit} unimplemented')
