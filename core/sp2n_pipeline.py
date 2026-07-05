"""
Dataset construction for nilpotent orbits in sp_{2n}.

This module generates, filters, and enriches the full table of symplectic
partitions of 2n together with their associated invariants (delta, local
rates, global rate) and conjecture verification flags.

The main entry point is :func:`create_sp2n_dataset`.
"""

import pandas as pd

from utils.partitions import Partition, a1, b1, generate_all_sp2n_partitions
from pipeline import Pipeline, PipelineBuilder
from .sp2n_helper import (
    delta,
    hypothesized_rate,
    indices_of_max_local_rate,
    local_rates_at_peaks,
    verify_hypothesis_3_3_3,
    verify_hypothesis_3_3_4,
)


def sp2n_pipeline(n: int, path_to_save: str) -> Pipeline:
    """Build the partition dataset for sp_{2n}.

    Parameters
    ----------
    n:
        The rank of the Lie algebra sp_{2n}.
    path_to_save:
        The file path where the dataset will be saved.
    """
    if n <= 1:
        raise ValueError("The rank n of the algebra must  be >= 2.")

    pipeline_builder = (
        PipelineBuilder()
        .create("Partition", generate_all_sp2n_partitions, n=n)
        .then(exclude_regular_and_trivial_partitions)
        
        .compute("a_1", a1, source_cols=["Partition"])
        .compute("b_1", b1, source_cols=["Partition"])
        .compute("Parts", lambda p: sorted(p.keys(), reverse=True), source_cols=["Partition"])
        .compute("Multiplicities", lambda p: [p[a] for a in sorted(p.keys(), reverse=True)], source_cols=["Partition"])

        .compute("Local Rates at Peaks", lambda p: local_rates_at_peaks(p, n), source_cols=["Partition"])
        .compute("Rate", lambda lrap: max(lrap.values()), source_cols=["Local Rates at Peaks"])
        .compute("Delta", delta, source_cols=["Partition"])
        .compute("r_delta", lambda df: df["Rate"] * df["Delta"], vectorized=True)
        .compute("Global Rate Indices", indices_of_max_local_rate, source_cols=["Local Rates at Peaks", "Rate"])
        .compute("Peaks", lambda lrap: list(lrap.keys()), source_cols=["Local Rates at Peaks"])

        .verify("WSXDH", lambda df: df["r_delta"] <= (2 * (n ** 2)), vectorized=True)

        .compute("Previous Partition's Rate", lambda df: df["Rate"].shift(1, fill_value=float("inf")), vectorized=True)
        .verify("Hypothesis 1.4 (local check)", lambda df: df["Rate"] <= df["Previous Partition's Rate"], vectorized=True)

        .compute("r_b_1", lambda df: hypothesized_rate(df["a_1"], df["b_1"], n), vectorized=True)
        .verify("Hypothesis 1.5", lambda df: df["Rate"] == df["r_b_1"], vectorized=True)

         # Independent check of Hypothesis 1.5
        .compute("First Global Rate Index", lambda lst: lst[0], source_cols=["Global Rate Indices"])
        .verify("b_1 Maximizes Local Rate", lambda df: df["b_1"] == df["First Global Rate Index"], vectorized=True)

        # Hypothesis 3.3.3: local rates are non-increasing along the peaks.
        .verify("Hypothesis 3.3.3", verify_hypothesis_3_3_3, source_col="Local Rates at Peaks")

        # Hypothesis 3.3.4: the maximum local rate is achieved uniquely at b_1
        # (up to the exceptional partition families).
        .verify("Hypothesis 3.3.4",
            lambda df: df.apply(lambda row: verify_hypothesis_3_3_4(row["Parts"], row["Local Rates at Peaks"], row["b_1"], row["Rate"]), axis=1),
            vectorized=True)

        .then(add_regular_and_trivial_partitions, n=n)
        .compute("Label", lambda p: get_label(p, n), source_cols=["Partition"])
        .save(path_to_save)
    )

    return pipeline_builder.build_pipeline()


def exclude_regular_and_trivial_partitions(dataset: pd.DataFrame) -> pd.DataFrame:
    return dataset[1:-1]


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
        "Partition": {2 * n: 1},
        "a_1":       2 * n,
        "b_1":       1,
        "Delta":     0,
        "Peaks":     list(range(1, n + 1)),
    }])
    trivial = pd.DataFrame([{
        "Partition": {1: 2 * n},
        "a_1":       1,
        "b_1":       2 * n,
        "Rate":      2.0,
        "Delta":     n ** 2,
        "r_delta":   2 * (n ** 2),
        "Peaks":     [],
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
