"""
Command-line script to verify the conjectures of Chapter 3 of the Thesis for sp_{2n}.

For each integer n in the given range, the script builds the partition dataset
and checks six conjecture columns, reporting pass/fail in colour.  A summary
table is printed after all values of n have been processed.

Usage
-----
From the repository root (after ``pip install -e .[dev]``)::

    python -m run.verify_conjectures <min_n> <max_n>

or via the installed console script::

    verify-conjectures <min_n> <max_n>

Example
-------
Verify all conjectures for n = 2, 3, ..., 50::

    verify-conjectures 2 50
"""

import sys

from rich.table import Table

from core.sp2n_pipeline import create_sp2n_dataset
from pandas import DataFrame
from utils.styles import console


def to_string_color_coded(value: bool) -> str:
    """Return *value* as a colour-coded rich markup string."""
    return f"[green]{value}[/green]" if value else f"[red]{value}[/red]"


def verify_hypothesis(data: DataFrame, hypothesis_name: str, n: int) -> bool:
    """Print and return whether *hypothesis_name* holds for all rows (partitions) of *data* at rank *n*.

    Parameters
    ----------
    data:
        The conjecture-verification DataFrame for a specific value of *n*,
        as returned by :func:`calculate.sp2n_data_supplier.create_sp2n_dataset`
        with ``verify_conjectures=True``.
        Must contain a boolean column named *hypothesis_name*.
    hypothesis_name:
        The name of the boolean column to check.
    n:
        The rank parameter, used only for the printed output line.

    Returns
    -------
    bool
        ``True`` if the hypothesis holds for every partition in *data*.
    """
    hypothesis_holds = bool(data[hypothesis_name].all())
    console.print(f"n={n}. {hypothesis_name} holds: {to_string_color_coded(hypothesis_holds)}")
    return hypothesis_holds


def main() -> None:
    """Parse arguments and run conjecture verification."""
    min_n = int(sys.argv[1])
    max_n = int(sys.argv[2])

    hypotheses_to_verify = [
        "Hyp_1.5",
        "rate_monotone",
        "WSXDH",
        "b1_maximizes_local_rate",
        "Hyp_3.3.3",
        "Hyp_3.3.4",
    ]
    verified_cases: dict[int, dict[str, bool]] = {}

    for n in range(min_n, max_n + 1):
        data = create_sp2n_dataset(n, verify_conjectures=True)
        verified_cases[n] = {
            hyp: verify_hypothesis(data, hyp, n)
            for hyp in hypotheses_to_verify
        }
        console.print("-" * 50)

    table = Table(title=f"Summary: n = {min_n} to {max_n}")
    table.add_column("Hypothesis", style="bold")
    table.add_column("Holds for all n")
    for hyp in hypotheses_to_verify:
        holds_for_all_n = all(verified_cases[n][hyp] for n in range(min_n, max_n + 1))
        table.add_row(hyp, to_string_color_coded(holds_for_all_n))
    console.print(table)


if __name__ == "__main__":
    main()
