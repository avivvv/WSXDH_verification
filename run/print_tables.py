"""
Command-line script for LaTeX table generation.

Generates a ``.tex`` file containing formatted tables of nilpotent orbit data
for sp_{2n}, written to the ``results/`` directory.

Usage
-----
From the repository root (after ``pip install -e .``)::

    python -m run.print_tables <n>              # single table for sp_{2n}
    python -m run.print_tables <min_n> <max_n>  # range of tables

or via the installed console script::

    print-tables <n>
    print-tables <min_n> <max_n>

Example
-------
Generate tables for sp_4, sp_6, ..., sp_10::

    print-tables 2 5
"""

import sys

from latex.latex_document_generator import generate_table_tex_for, generate_tables_tex_for_range


def main() -> None:
    """Parse arguments and dispatch to the appropriate table generator."""
    if len(sys.argv) == 2:
        generate_table_tex_for(int(sys.argv[1]))
    else:
        generate_tables_tex_for_range(int(sys.argv[1]), int(sys.argv[2]))


if __name__ == "__main__":
    main()
