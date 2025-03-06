def to_dict(partition: list[int]) -> dict[int, int]:
    if isinstance(partition, dict): # partition is already in power notation
        return partition.copy();

    return {x: partition.count(x) for x in set(partition)};


def to_list(partition: dict[int, int]) -> list[int]:
    if isinstance(partition, list): # partition is already in sequence notation
        return partition[:];

    return [x for sublist in [b * [a] for a, b in partition.items()] for x in sublist];


def tostring_as_power(partition):
    p_as_tuples = sorted(to_dict(partition).items(), key=lambda x: x[0], reverse=True);
    power_strings = [str(a) if b <= 1 else str(a) + "^{" + str(b) + "}" for a,b in p_as_tuples];

    return "[" + ", ".join(power_strings) + "]";


def tostring_as_sequence(partition):
    p = to_list(partition);
    num_strings = [str(d) for d in p];

    return "[" + ", ".join(num_strings) + "]";


def validate_partition(partition: dict[int,int], n: int):
    if n <= 1:
        raise ValueError(f"n must be >= 2. instead it was {n}.")

    p = to_list(partition);

    if sum(p) != 2*n:
        raise ValueError(f"error: {p} is not a partition of 2n={2*n}")
    
    for a,b in to_dict(p).items():
        if a % 2 != 0 and b % 2 != 0:
            raise ValueError(f"odd element of the partition ({a}) had odd multiplicity ({b}) in partition {tostring_as_sequence(p)}.")
