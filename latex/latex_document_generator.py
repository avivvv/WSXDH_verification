import os
from pylatex import Document, Section, NoEscape, NewPage, Package
from .latex_table_generator import generate_tex_table
from calculate.sp2n_data_supplier import create_sp2n_data__n_equals

_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')


def generate_table_tex_for(n: int):
    tex_filename = os.path.join(_RESULTS_DIR, f"tables__sp{2*n}")
    generate(n, n, tex_filename)


def generate_tables_tex_for_range(min_n: int, max_n: int):
    tex_filename = os.path.join(_RESULTS_DIR, f"tables__sp{2*min_n}-sp{2*max_n}")
    generate(min_n, max_n, tex_filename)


def generate(min_n: int, max_n: int, tex_filename: str):
    doc = Document()
    doc.packages.append(Package('longtable'))
    doc.packages.append(Package('geometry', 'a4paper,margin=0.1in,footskip=1in'))


    for n in range(min_n, max_n+1): # range is inclusive.
        data = create_sp2n_data__n_equals(n, printable_version=True)
        table = generate_tex_table(data, n)

        with doc.create(Section(NoEscape("$\mathfrak{sp}_{" + str(2*n) + "}$"), label=False)):
            doc.append(NoEscape(table))
            doc.append(NewPage())

    doc.generate_tex(tex_filename)    
    print(f"tex file saved as {tex_filename}.tex")






