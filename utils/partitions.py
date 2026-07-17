"""
Utility functions for representing, generating, and inspecting partitions that parametrize
nilpotent orbits in the symplectic Lie algebra sp_{2n}.

Partitions are encoded as dictionaries mapping each distinct part *a* to
its multiplicity *b*, i.e. ``{a_1: b_1, a_2: b_2, ...}`` with parts listed in
decreasing order ``a_1 > a_2 > ... > a_k``.
"""

from sympy.combinatorics import IntegerPartition


# Type alias used throughout the package.
Partition = dict[int, int]


def generate_all_sp2n_partitions(n: int) -> list[Partition]:
    """Return all symplectic partitions of 2n in reverse-lexicographic order.

    A partition of 2n is *symplectic* (of type C) if every odd part occurs
    with even multiplicity. These are precisely the partitions that label
    nilpotent orbits in sp_{2n} (see [CM93, Theorem 5.1.3]).

    Parameters
    ----------
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    list[Partition]
        All symplectic partitions of 2n, listed in reverse-lexicographic
        order, starting with the regular partition ``{2n: 1}`` and ending
        with the trivial partition ``{1: 2n}``.
    """
    regular = IntegerPartition([2 * n])
    p = regular.copy()
    all_partitions: list[Partition] = []
    first_run = True
    while p != regular or first_run:
        partition = p.as_dict()
        if all(b % 2 == 0 for a, b in partition.items() if a % 2 == 1):
            all_partitions.append(partition)
        p = p.prev_lex()
        first_run = False

    return all_partitions


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


def parts(partition: Partition) -> list[int]:
    """Return the parts of *partition* in decreasing order.

    Parameters
    ----------
    partition:
        A non-empty partition encoded as ``{a_j: b_j}``.
    Returns
    -------
    list[int]
        The parts of the partition, sorted in decreasing order.
    """
    return sorted(partition.keys(), reverse=True)


def multiplicities(partition: Partition) -> list[int]:
    """Return the multiplicities of *partition* in decreasing order of parts.

    Parameters
    ----------
    partition:
        A non-empty partition encoded as ``{a_j: b_j}``.
    Returns
    -------
    list[int]
        The multiplicities of the partition, sorted in decreasing order of parts.
    """
    return [partition[a] for a in parts(partition)]