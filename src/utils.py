def time_units_transform(unit: str, times_ns: list[int]):
    match unit:
        case "s":
            return list(map(lambda x: x / 1_000_000_000, times_ns))
        case _:
            raise Exception(f"time unit transform for unit: {unit} unimplemented")
