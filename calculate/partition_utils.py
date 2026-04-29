def a1(partition: dict[int, int]) -> int:
    return max(partition.keys())


def b1(partition: dict[int, int]) -> int:
    return partition[a1(partition)]


def tostring(partition):
    ab_pairs = sorted(partition.items(), key=lambda x: x[0], reverse=True)
    power_notation_strings = [str(a) + ("" if b == 1 else "^{" + str(b) + "}") for a,b in ab_pairs]

    return "[" + ", ".join(power_notation_strings) + "]"
