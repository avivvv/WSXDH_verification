"""
Utility functions for representing and inspecting partitions that parametrize
nilpotent orbits in the symplectic Lie algebra sp_{2n}.

Partitions are encoded as dictionaries mapping each distinct part *a* to
its multiplicity *b*, i.e. ``{a_1: b_1, a_2: b_2, ...}`` with parts listed in
decreasing order ``a_1 > a_2 > ... > a_k``.
"""

# Type alias used throughout the package.
Partition = dict[int, int]


def a1(partition: Partition) -> int:
    """Return the largest part of *partition*.

    Parameters
    ----------
    partition:
        A non-empty partition encoded as ``{a_j: b_j}``.

    Returns
    -------
    int
        The value ``a_1 = max{a : (a, b) in partition}``.
    """
    return max(partition.keys())


def b1(partition: Partition) -> int:
    """Return the multiplicity of the largest part of *partition*.

    Parameters
    ----------
    partition:
        A non-empty partition encoded as ``{a_j: b_j}``.

    Returns
    -------
    int
        The multiplicity ``b_1`` of the largest part ``a_1``.
    """
    return partition[a1(partition)]


def format_partition(partition: Partition) -> str:
    """Format *partition* in the LaTeX power notation used in the tables.

    Parts are listed in decreasing order.
    A part with multiplicity 1 is written without an exponent.

    Parameters
    ----------
    partition:
        A partition encoded as ``{a_j: b_j}``.

    Returns
    -------
    str
        A string of the form ``[a_1^{b_1}, a_2^{b_2}, ...]``.

    Example
    --------
    >>> format_partition({4: 1, 2: 3})
    '[4, 2^{3}]'
    """
    ab_pairs = sorted(partition.items(), key=lambda x: x[0], reverse=True)
    power_notation_strings = [
        str(a) if b == 1 else f"{a}^{{{b}}}"
        for a, b in ab_pairs
    ]
    return "[" + ", ".join(power_notation_strings) + "]"
