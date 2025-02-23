from fractions import Fraction
import math
from calculate.rate_calculator import rate
from calculate.delta_calculator import delta
from calculate.partition_utils import to_list, tostring_as_power
from calculate.sp2n_data_supplier import generate_all_partitions


def generate_latex_table_for_rank(n: int):
    dimension = str(2*n);

    table_start = """
    \\begin{center}
    \\label{table:sp_""" + dimension + """}
    \\begin{longtable}{||c|c|c|c|c||}
    \\caption{$r(\\sigma)$ and $\\delta(\\sigma)$ for representations $\\sigma: \\mathfrak{sl}_2 \\to \\mathfrak{sp}_{""" + dimension + """}$}
    \\hline
    Partition $\\textbf{d}_\\sigma$
    &$C^{-1} \\cdot \\Delta(\\textbf{d}_\\sigma)$
    &$r(\\sigma)$
    &$\\delta(\\sigma)$
    &$r(\\sigma) \\cdot \\delta(\\sigma)$
    \\\\ [0.3ex] \\hline\\endhead
    """

    table_end = """
    \\end{longtable}
    \\end{center}
    """
        
    table_rows = []
    delimiter = " & "
    row_end = " \\\\ \\hline "
    for partition in generate_all_partitions(n):
        is_not_reg = to_list(partition) != [2*n];

        p_as_string = tostring_as_power(partition)
        cartan_inverse_times_dynkin_weights = [2,2,2,2,2,2] #wrongggg
        citdw_as_string = f"({",".join([str(x) for x in cartan_inverse_times_dynkin_weights])})"
        r = rate(partition, n) if is_not_reg else None
        delt = delta(partition, n)
        
        table_rows.append(delimiter.join([
            f"${p_as_string}$",
            f"${citdw_as_string}$",
            f"${format_frac(r) if is_not_reg else "\\infty"}$",
            f"${format_frac(delt)}$",
            f"${format_frac(r*delt)}$" if is_not_reg else "NA"
        ]) + row_end)
    
    return table_start + f"\n".join(table_rows) + table_end


def format_frac(num: float) -> str:
    frac = Fraction(num).limit_denominator()

    if frac.is_integer():
        return format(frac, '');

    int_val = math.floor(num);

    return f"{str(int_val)} < {format(frac, '')} < {str(int_val+1)}"