"""
This module implements the main invariants of a symplectic partition that appear in the thesis:

* :func:`delta` - introduced in Definition 1.2, and supplied with a formula in Proposition 3.1.10.
* :func:`diagonal_values_at_peaks` - the diagonal of the dominant semisimple representative
    of the sl_2 triple, computed at each peak. Recall that peaks were introduced in Definition 3.2.2,
    and we can compute them from Lemmas 3.2.6 and 3.2.9.
* :func:`local_rates_at_peaks` - the local rate r_p (introduced in Definition 3.2.1) calculated at each peak.

It also provides the conjecture-checking helpers used by
:mod:`calculate.sp2n_data_supplier`.
"""

from .partition_utils import Partition, a1, b1


def delta(partition: Partition) -> int:
    """Compute delta(d) from Proposition 3.1.10.

    Parameters
    ----------
    partition:
        A symplectic partition encoded as ``{part: multiplicity}``.

    Returns
    -------
    int
        The non-negative integer ``delta(d)``.
    """
    part_counts = partition.items()
    b_where_a_is_even = [b for a, b in part_counts if a % 2 == 0]
    b_which_are_odd = [b for a, b in part_counts if b % 2 == 1]
    sum_of_b_squared = sum(b**2 for a,b in part_counts)

    return int((sum_of_b_squared / 4) + (len(b_which_are_odd) / 4) - (sum(b_where_a_is_even) / 2))


def diagonal_values_at_peaks(partition: Partition) -> dict[int, int]:
    """Compute the value h_p at each peak p of the partition.

    It suffices to record the diagonal value at each peak, since the diagonal
    is constant between consecutive peaks (see Definition 3.2.2).
    See also Recipe 2.2.35 for the original construction of the dominant diagonal.

    Parameters
    ----------
    partition:
        A symplectic partition encoded as ``{part: multiplicity}``.

    Returns
    -------
    dict[int, int]
        A dictionary ``{p: h_p}`` whose keys are the peak indices of the
        partition and whose values are the diagonal entries h_p at
        those peaks, in decreasing order of p.
    """
    parts = list(partition.keys())
    even_parts = [a_j for a_j in parts if a_j % 2 == 0]
    odd_parts  = [a_j for a_j in parts if a_j % 2 == 1]

    diagonal_values_by_peak: dict[int, int] = {}
    current_peak = 0

    # h ranges over possible diagonal values on the positive half of the
    # diagonal. Each part a_j > h with a_j ≠ h (mod 2) contributes one
    # occurrence of h to the diagonal (see Lemma 3.2.6 for the set J(h)).
    # h = 0 is excluded because h_p ≠ 0 at every peak by definition.
    for h in range(a1(partition) - 1, 0, -1):
        # J(h) = {a_j : a_j > h  and  a_j ≡ h (mod 2)}, from Lemma 3.2.6.
        parts_of_relevant_parity = odd_parts if h % 2 == 0 else even_parts
        parts_in_J_of_h = [a_j for a_j in parts_of_relevant_parity if a_j > h]
        if not parts_in_J_of_h:
            continue

        multiplicity_sum = sum(partition[a_j] for a_j in parts_in_J_of_h)
        current_peak += multiplicity_sum
        diagonal_values_by_peak[current_peak] = h

    return diagonal_values_by_peak


def local_rates_at_peaks(partition: Partition, n: int) -> dict[int, float]:
    """Compute the local rate r_p(d) at each peak p of the partition.

    The local rate at peak p is given in Definition 3.2.1 as

    .. math::

        r_p(\\mathbf{d}) = \\frac{4np - 2p^2}
                                  {2np - p^2 - \\sum_{k \\le p} h_k(\\mathbf{d})},

    where the sum in the denominator runs over all diagonal entries h_k up
    to and including position p.

    Parameters
    ----------
    partition:
        A symplectic partition of 2n encoded as ``{part: multiplicity}``.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    dict[int, float]
        A dictionary ``{p: r_p}`` whose keys are the peak indices and whose
        values are the local rates, in decreasing order of p.
    """
    diagonal_values_by_peak = diagonal_values_at_peaks(partition)
    peaks = sorted(diagonal_values_by_peak.keys())
    previous_peak = 0
    sum_of_h_k = 0
    local_rates_by_peak: dict[int, float] = {}

    for p in peaks:
        h_p = diagonal_values_by_peak[p]
        sum_of_h_k += h_p * (p - previous_peak)
        sum_of_reg_h_k = 2 * n * p - p ** 2
        local_rates_by_peak[p] = (2 * sum_of_reg_h_k) / (sum_of_reg_h_k - sum_of_h_k)
        previous_peak = p

    return local_rates_by_peak


def verify_hypothesis_3_3_4(
    parts: list[int],
    local_rates_by_peak: dict[int, float],
    b_1: int,
    rate: float,
) -> bool:
    """Check whether Hypothesis 3.3.4 holds for the given partition data.

    Hypothesis 3.3.4 asserts that the global maximum rate r(d) is achieved
    uniquely at the peak indexed by b_1, with the exception of partitions of
    the form ``[a^b]`` or ``[a^b, (a-1)^c]`` (at most two distinct part
    values differing by at most 1).

    Parameters
    ----------
    parts:
        The list of distinct part values of the partition.
    local_rates_by_peak:
        The local rates ``{p: r_p}`` as returned by
        :func:`local_rates_at_peaks`.
    b_1:
        The multiplicity of the largest part (the conjectured maximiser).
    rate:
        The global maximum rate ``r(d) = max_p r_p``.

    Returns
    -------
    bool
        ``True`` if the hypothesis holds or the partition belongs to an
        exceptional family; ``False`` otherwise.
    """
    if len(parts) <= 2 and (max(parts) - min(parts) <= 1):
        return True
    return all(p == b_1 or r_p < rate for p, r_p in local_rates_by_peak.items())


def indices_of_max_local_rate(
    local_rates_by_peak: dict[int, float],
    rate: float,
) -> list[int]:
    """Return all peak indices at which the local rate equals the maximum.

    Parameters
    ----------
    local_rates_by_peak:
        The local rates ``{p: r_p}`` as returned by
        :func:`local_rates_at_peaks`.
    rate:
        The global maximum rate to match.

    Returns
    -------
    list[int]
        A list of peak indices ``p`` for which ``r_p == rate``.
    """
    return [p for p, r_p in local_rates_by_peak.items() if r_p == rate]


def hypothesized_rate(a_1: int, b_1: int, n: int) -> float:
    """Return the value of the rate formula from Hypothesis 1.5.

    If Hypothesis 1.5 holds for the partition with leading part ``a_1`` and
    multiplicity ``b_1``, then the actual rate r(d) equals r_{b_1}(d) and is given by:

    .. math::

        r(\\mathbf{d}) = r_{b_1}(\\mathbf{d}) = \\frac{4n - 2b_1}{2n - a_1 - b_1 + 1}.

    Parameters
    ----------
    a_1:
        The largest part of the partition.
    b_1:
        The multiplicity of the largest part.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    float
        The conjectured rate value.

    Notes
    -----
    This function also accepts :class:`pandas.Series` arguments, in which
    case the return value is a Series (pandas applies element-wise division).
    """
    return (4 * n - 2 * b_1) / (2 * n - a_1 - b_1 + 1)
