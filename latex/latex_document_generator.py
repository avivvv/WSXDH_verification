from pylatex import Document, Section, Math, NoEscape, NewPage, LineBreak, Package
from latex.latex_table_generator import generate_latex_table_for_rank as table


def generate_tables_pdf_for_range(min_n: int, max_n: int):
    pdf_filename = f"tables__sp{2*min_n}-sp{2*max_n}"
    doc = Document();
    doc.packages.append(Package('longtable'));
    doc.packages.append(Package('geometry', 'a4paper,margin=0.1in,footskip=1in'));


    for n in range(min_n, max_n+1):
        with doc.create(Section(NoEscape("$\mathfrak{sp}_{" + str(2*n) + "}$"), label=False)):
            doc.append(Section(NoEscape(f"For $n={n}$, our goal is to have $r(\sigma) \cdot \delta(\sigma) \leq 2n^2 = {2*(n**2)} \quad \\forall \sigma$."), numbering=False, label=False))
            doc.append(LineBreak())
            
            doc.append(NoEscape(table(n)))
            doc.append(NewPage())

    doc.generate_tex(pdf_filename)

    
    print(f"tex file saved as {pdf_filename}.tex")






