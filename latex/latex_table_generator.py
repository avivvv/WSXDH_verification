from fractions import Fraction
import math
import pandas as pd
from calculate.partition_utils import tostring


def generate_tex_table(partitions: pd.DataFrame, n: int):
    dimension = str(2*n)

    table_start = """
    \\begin{center}
    \\label{table:sp_""" + dimension + """}
    \\begin{longtable}{||c|c|c|c|c|c|c||}
    \\hline
    Partition \\textbf{d}
    &Peaks
    &$\\operatorname{argmax}\\, r_i(\\textbf{d})$
    &$r(\\textbf{d})$
    &$\\delta(\\textbf{d})$
    &$r(\\textbf{d}) \\cdot \\delta(\\textbf{d})$
    &Remarks
    \\\\ [0.3ex] \\hline\\endhead
    """

    table_end = """
    \\end{longtable}
    \\end{center}
    """
        
    table_rows = []
    delimiter = " & "
    row_end = " \\\\ \\hline "
    for partition in partitions.to_dict(orient="records"):
        p = partition['Partition']
        is_not_reg = p != {(2*n): 1}
        is_not_triv = p != {1: 2*n}

        p_as_string = tostring(p)
        max_i = ",".join([str(num) for num in partition['max_indices']]) if is_not_reg else None
        peaks = ",".join([str(num) for num in partition['Peaks']])
        r = partition['Rate'] if is_not_reg else None
        delt = partition['Delta']
        remarks = partition['Remarks']
        
        table_rows.append(delimiter.join([
            f"${p_as_string}$",
            f"${peaks}$" if is_not_triv else "NA",
            f"${max_i}$" if is_not_reg else "NA",
            f"${format_number(r) if is_not_reg else "\\infty"}$",
            f"${format_number(delt)}$",
            f"${format_number(r*delt)}$" if is_not_reg else "NA",
            remarks if remarks != '' else '-'
        ]) + row_end)
    
    return table_start + f"\n".join(table_rows) + table_end


def format_number(num: float) -> str:
    frac = Fraction(num).limit_denominator()

    if frac.is_integer():
        return format(frac, '')

    int_val = math.floor(num)

    return f"{str(int_val)} < {format(frac, '')} < {str(int_val+1)}"