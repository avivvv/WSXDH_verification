import math
from fractions import Fraction
from utils.partitions import Partition


def format_partition(partition: Partition) -> str:
    """Format *partition* in power notation.

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
