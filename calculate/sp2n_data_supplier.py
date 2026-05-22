"""
Dataset construction for nilpotent orbits in sp_{2n}.

This module generates, filters, and enriches the full table of symplectic
partitions of 2n together with their associated invariants (delta, local
rates, global rate) and conjecture verification flags.

The main entry point is :func:`create_sp2n_dataset`.
"""

import pandas as pd
from sympy.combinatorics.partitions import IntegerPartition

from calculate.partition_utils import Partition, a1, b1
from .sp2n_calculator import (
    delta,
    hypothesized_rate,
    indices_of_max_local_rate,
    local_rates_at_peaks,
    verify_hypothesis_3_3_4,
)


def create_sp2n_dataset(
    n: int,
    verify_conjectures: bool = False,
    printable_version: bool = False,
) -> pd.DataFrame:
    """Build the partition dataset for sp_{2n}.

    Parameters
    ----------
    n:
        The rank of the Lie algebra sp_{2n}.
    verify_conjectures:
        If ``True``, enrich the dataset with conjecture-verification boolean
        columns (Hyp_1.5, rate_monotone, WSXDH, b1_maximizes_local_rate,
        Hyp_3.3.3, Hyp_3.3.4). Mutually exclusive with *printable_version*.
    printable_version:
        If ``True``, enrich the dataset with display columns (Peaks, Remarks)
        and include the regular and trivial partitions as boundary rows.
        Mutually exclusive with *verify_conjectures*.

    Returns
    -------
    pd.DataFrame
        A DataFrame whose rows correspond to symplectic partitions of 2n.
        Base columns: Partition, a_1, b_1, local_rates_at_peaks, Rate,
        Delta, r_delta, max_indices.
    """
    partitions = generate_all_partitions(n)
    data = generate_basic_data(partitions, n)
    if verify_conjectures and printable_version:
        raise ValueError("The parameters 'verify_conjectures' and 'printable_version' are mutually exclusive.")
    if verify_conjectures:
        return enrich_sp2n_data_for_verification(data, n)
    if printable_version:
        return enrich_sp2n_data_for_printing(data, n)
    return data


def generate_all_partitions(n: int) -> list[Partition]:
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
    reg = IntegerPartition([2 * n])
    p = reg.copy()
    all_partitions: list[Partition] = []
    first_run = True
    while p != reg or first_run:
        partition = p.as_dict()
        if all(b % 2 == 0 for a, b in partition.items() if a % 2 == 1):
            all_partitions.append(partition)
        p = p.prev_lex()
        first_run = False

    return all_partitions


def generate_basic_data(all_partitions: list[Partition], n: int) -> pd.DataFrame:
    """Construct the base DataFrame for the non-regular non-trivial symplectic partitions.

    The regular partition ``{2n: 1}`` (first in *all_partitions*) and the
    trivial partition ``{1: 2n}`` (last) are excluded here.

    Parameters
    ----------
    all_partitions:
        All symplectic partitions of 2n, as returned by :func:`generate_all_partitions`.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Partition, a_1, b_1, local_rates_at_peaks,
        Rate, Delta, r_delta, max_indices.
    """
    partitions = all_partitions[1:-1]  # Exclude regular and trivial partitions
    dataset = pd.DataFrame({
        "Partition": partitions,
        "a_1": [a1(partition) for partition in partitions],
        "b_1": [b1(partition) for partition in partitions],
    })
    dataset["local_rates_at_peaks"] = dataset["Partition"].map(
        lambda partition: local_rates_at_peaks(partition, n)
    )
    dataset["Rate"] = dataset["local_rates_at_peaks"].map(lambda d: max(d.values()))
    dataset["Delta"] = dataset["Partition"].map(delta)
    dataset["r_delta"] = dataset["Rate"] * dataset["Delta"]
    dataset["max_indices"] = [
        indices_of_max_local_rate(local_rates_by_peak, rate)
        for local_rates_by_peak, rate in zip(
            dataset["local_rates_at_peaks"], dataset["Rate"]
        )
    ]
    return dataset


def enrich_sp2n_data_for_printing(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    """Add display columns and boundary rows for LaTeX table generation.

    Parameters
    ----------
    dataset:
        The base DataFrame returned by :func:`generate_basic_data`.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    pd.DataFrame
        The enriched DataFrame with the additional columns 'Peaks' and 'Remarks',
        and with the regular and trivial partition rows added.
    """
    dataset["Peaks"] = dataset["local_rates_at_peaks"].map(
        lambda local_rates_by_peak: local_rates_by_peak.keys()
    )
    dataset = add_regular_and_trivial_partitions(dataset, n)
    dataset["Remarks"] = dataset["Partition"].map(
        lambda partition: get_label(partition, n)
    )
    return dataset


def enrich_sp2n_data_for_verification(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    """Add conjecture-verification boolean columns to *dataset*.

    Parameters
    ----------
    dataset:
        The base DataFrame returned by :func:`generate_basic_data`.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    pd.DataFrame
        The enriched DataFrame with additional columns: hypothesized_rate,
        Hyp_1.5, rate_monotone, WSXDH, b1_maximizes_local_rate, Hyp_3.3.3, Hyp_3.3.4.
    """
    # Since hypothesized_rate performs only arithmetic, it supports pandas vectorisation directly.
    dataset["hypothesized_rate"] = hypothesized_rate(dataset["a_1"], dataset["b_1"], n)
    dataset["Hyp_1.5"] = dataset["Rate"] == dataset["hypothesized_rate"]  # Hypothesis 1.5

    prev_lex_rate = dataset["Rate"].shift(1, fill_value=float("inf"))
    dataset["rate_monotone"] = dataset["Rate"] <= prev_lex_rate  # Hypothesis 1.4 (local check)

    WSXDH_bound = 2 * (n ** 2)
    dataset["WSXDH"] = dataset["r_delta"] <= WSXDH_bound  # Hypothesis 1.3

    first_max = dataset["max_indices"].apply(lambda lst: lst[0] if lst else 0)
    dataset["b1_maximizes_local_rate"] = dataset["b_1"] == first_max # Independent check of Hypothesis 1.5

    # Hypothesis 3.3.3: local rates are non-increasing along the peaks.
    dataset["Hyp_3.3.3"] = dataset["local_rates_at_peaks"].map(
        lambda d: all(r_i >= r_j for r_i, r_j in zip(d.values(), list(d.values())[1:]))
    )

    # Hypothesis 3.3.4: the maximum local rate is achieved uniquely at b_1
    # (up to the exceptional partition families).
    dataset["Hyp_3.3.4"] = [
        verify_hypothesis_3_3_4(
            list(partition.keys()), local_rates_by_peak, b_1_val, rate
        )
        for partition, local_rates_by_peak, b_1_val, rate in zip(
            dataset["Partition"],
            dataset["local_rates_at_peaks"],
            dataset["b_1"],
            dataset["Rate"],
        )
    ]
    return dataset


def add_regular_and_trivial_partitions(
    dataset: pd.DataFrame,
    n: int,
) -> pd.DataFrame:
    """Prepend the regular partition row and append the trivial partition row.

    Parameters
    ----------
    dataset:
        The enriched DataFrame including all basic columns as well as `Peaks`.
    n:
        The rank of the Lie algebra sp_{2n}.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with the regular partition as the first row and the
        trivial partition as the last row.
    """
    regular = pd.DataFrame([{
        "Partition":            {2 * n: 1},
        "a_1":                  2 * n,
        "b_1":                  1,
        "local_rates_at_peaks": None,
        "Rate":                 None,
        "Delta":                0,
        "r_delta":              None,
        "max_indices":          None,
        "Peaks":                list(range(1, n + 1)),
    }])
    trivial = pd.DataFrame([{
        "Partition":            {1: 2 * n},
        "a_1":                  1,
        "b_1":                  2 * n,
        "local_rates_at_peaks": None,
        "Rate":                 2.0,
        "Delta":                n ** 2,
        "r_delta":              2 * (n ** 2),
        "max_indices":          list(range(1, n + 1)),
        "Peaks":                [],
    }])
    return pd.concat([regular, dataset, trivial], ignore_index=True)


def get_label(partition: Partition, n: int) -> str:
    """Generate a descriptive label for *partition*.

    Parameters
    ----------
    partition:
        A symplectic partition of 2n.
    n:
        The rank parameter.

    Returns
    -------
    str
        A descriptive label for the partition.
        Returns an empty string if no special label applies.
    """
    if partition == {2 * n: 1}:
        return "Principal"
    if partition == {1: 2 * n}:
        return "Trivial"
    if partition == {2 * n - 2: 1, 2: 1}:
        return "Subregular"
    if partition == {2: 1, 1: 2 * n - 2}:
        return "Minimal"
    if len(partition) == 1:
        return r"$[a^b]$"
    if len(partition) == 2:
        keys = set(partition.keys())
        if keys == {1, 2}:
            return r"$[2^b, 1^c]$"
        if max(keys) - min(keys) == 1:
            return r"$[a^b, (a-1)^c]$"
        if 1 in keys:
            return r"$[a^b, 1^c]$"
    return ""
