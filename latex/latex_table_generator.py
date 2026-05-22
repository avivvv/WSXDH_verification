"""
LaTeX table generation for the sp_{2n} nilpotent orbit data.

This module converts a :class:`pandas.DataFrame` produced by
:mod:`calculate.sp2n_data_supplier` into a ``longtable`` LaTeX environment.
"""

import math
from fractions import Fraction

import pandas as pd

from calculate.partition_utils import Partition, format_partition


def generate_tex_table(partitions: pd.DataFrame, n: int) -> str:
    """Generate a LaTeX ``longtable`` string for the sp_{2n} orbit data.

    Parameters
    ----------
    partitions:
        A DataFrame as returned by
        :func:`calculate.sp2n_data_supplier.create_sp2n_dataset` with
        ``printable_version=True``.  Must contain the columns: Partition,
        Peaks, max_indices, Rate, Delta, r_delta, Remarks.
    n:
        The rank of the ambient Lie algebra sp_{2n}.

    Returns
    -------
    str
        A self-contained LaTeX snippet containing a ``longtable`` wrapped in
        a ``center`` environment.
    """
    dimension = str(2 * n)
    table_start = (
        "\n"
        "    \\begin{center}\n"
        "    \\label{table:sp_" + dimension + "}\n"
        "    \\begin{longtable}{||c|c|c|c|c|c|c||}\n"
        "    \\hline\n"
        "    Partition \\textbf{d}\n"
        "    &Peaks\n"
        "    &$\\operatorname{argmax}\\, r_i(\\textbf{d})$\n"
        "    &$r(\\textbf{d})$\n"
        "    &$\\delta(\\textbf{d})$\n"
        "    &$r(\\textbf{d}) \\cdot \\delta(\\textbf{d})$\n"
        "    &Remarks\n"
        "    \\\\ [0.3ex] \\hline\\endhead\n"
    )
    table_end = (
        "    \\end{longtable}\n"
        "    \\end{center}\n"
    )

    row_end = " \\\\ \\hline "
    table_rows: list[str] = []

    for record in partitions.to_dict(orient="records"):
        p: Partition = record["Partition"]
        is_regular = p == {2 * n: 1}
        is_trivial = p == {1: 2 * n}

        peaks_str = ",".join(str(num) for num in record["Peaks"])
        max_i_str = (
            ",".join(str(num) for num in record["max_indices"])
            if not is_regular else None
        )
        r: float | None = record["Rate"] if not is_regular else None
        delt: int = record["Delta"]
        remarks: str = record["Remarks"]

        table_rows.append(
            " & ".join([
                f"${format_partition(p)}$",
                f"${peaks_str}$" if not is_trivial else "NA",
                f"${max_i_str}$" if not is_regular else "NA",
                "$\\infty$" if is_regular else f"${format_number(r)}$",
                f"${format_number(delt)}$",
                "NA" if is_regular else f"${format_number(r * delt)}$",
                remarks if remarks != "" else "-",
            ])
            + row_end
        )

    return table_start + "\n".join(table_rows) + table_end


def format_number(num: float | int) -> str:
    """Format a number for display in a LaTeX table cell.

    If *num* is an integer it is returned as a string.
    Otherwise, since all numbers in the context of this project are rational,
    a string of the form ``"k < p/q < k+1"`` is returned, indicating that the value lies
    strictly between two consecutive integers. 

    Parameters
    ----------
    num:
        The value to format.

    Returns
    -------
    str
        The formatted string, e.g. ``'3'`` or ``'2 < 8/3 < 3'``.

    Examples
    --------
    >>> format_number(3.0)
    '3'
    >>> format_number(8 / 3)
    '2 < 8/3 < 3'
    """
    frac = Fraction(num).limit_denominator(10 ** 9)
    if frac.denominator == 1:
        return str(frac.numerator)
    int_val = math.floor(num)
    return f"{int_val} < {frac} < {int_val + 1}"
