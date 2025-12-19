def a1(partition: dict[int, int]):
    return max(partition.keys());


def b1(partition: dict[int, int]):
    return partition[a1(partition)];


def tostring(partition):
    p_as_tuples = sorted(partition.items(), key=lambda x: x[0], reverse=True);
    power_strings = [str(a) + ("" if b == 1 else "^{" + str(b) + "}") for a,b in p_as_tuples];

    return "[" + ", ".join(power_strings) + "]";


def to_list(partition: dict[int, int]) -> list[int]:
    return sorted([x for sublist in [b * [a] for a, b in partition.items()] for x in sublist]);


def validate_partition(partition: dict[int,int], n: int, lie_algebra = "sp2n"):
    if n <= 1:
        raise ValueError(f"n must be >= 2. instead it was {n}.")
    
    if sum(to_list(partition)) != 2*n:
        raise ValueError(f"error: {partition} is not a partition of 2n={2*n}")
    
    if lie_algebra == "sp2n":
        for a,b in partition.items():
            if a % 2 != 0 and b % 2 != 0:
                raise ValueError(f"odd element of the partition ({a}) had odd multiplicity ({b}) in partition {tostring(partition)}.")
