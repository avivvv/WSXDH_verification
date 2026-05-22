"""
TODO: make the docstrings make sense before merging.

High-level driver for generating LaTeX documents containing sp_{2n} tables.

This module provides convenience wrappers around
:func:`latex.latex_table_generator.generate_tex_table` that compile one or
more tables into a single ``.tex`` file written to the ``results/`` directory
at the repository root.
"""

import os

from pylatex import Document, NoEscape, NewPage, Package, Section

from .latex_table_generator import generate_tex_table
from calculate.sp2n_data_supplier import create_sp2n_dataset

_RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
)


def generate_table_tex_for(n: int) -> None:
    """Generate a single-table ``.tex`` file for sp_{2n}.

    The output file is written to the ``results/`` directory as
    ``tables__sp{2n}.tex``.

    Parameters
    ----------
    n:
        The rank parameter.
    """
    tex_filename = os.path.join(_RESULTS_DIR, f"tables__sp{2 * n}")
    _generate(n, n, tex_filename)


def generate_tables_tex_for_range(min_n: int, max_n: int) -> None:
    """Generate a multi-table ``.tex`` file for sp_{2*min_n} through sp_{2*max_n}.

    The output file is written to the ``results/`` directory as
    ``tables__sp{2*min_n}-sp{2*max_n}.tex``.

    Parameters
    ----------
    min_n:
        The smallest rank parameter to include.
    max_n:
        The largest rank parameter to include (inclusive).
    """
    tex_filename = os.path.join(
        _RESULTS_DIR, f"tables__sp{2 * min_n}-sp{2 * max_n}"
    )
    _generate(min_n, max_n, tex_filename)


def _generate(min_n: int, max_n: int, tex_filename: str) -> None:
    """Build and write the ``.tex`` document for a range of ranks.

    Parameters
    ----------
    min_n:
        The smallest rank parameter.
    max_n:
        The largest rank parameter (inclusive).
    tex_filename:
        Absolute path to the output file without the ``.tex`` extension;
        pylatex appends it automatically.
    """
    doc = Document()
    doc.packages.append(Package("longtable"))
    doc.packages.append(Package("geometry", "a4paper,margin=0.1in,footskip=1in"))
    doc.packages.append(Package("amsmath"))
    doc.packages.append(Package("amsfonts"))

    for n in range(min_n, max_n + 1):
        data = create_sp2n_dataset(n, printable_version=True)
        table = generate_tex_table(data, n)
        with doc.create(
            Section(NoEscape(r"$\mathfrak{sp}_{" + str(2 * n) + r"}$"), label=False)
        ):
            doc.append(NoEscape(table))
            doc.append(NewPage())

    doc.generate_tex(tex_filename)
    print(f"tex file saved as {tex_filename}.tex")
