from pylatex import Document, Section, Math, NoEscape, NewPage, LineBreak
from latex.latex_table_generator import generate_latex_table_for_rank as table


pdf_filename = "tables_sp2n"

def generate_tables_pdf_for_range(nums: list[int]):
    doc = Document();

    for n in nums:
        with doc.create(Section(NoEscape("$\mathfrak{sp}_{" + str(2*n) + "}$"))):
            doc.append("For ")
            doc.append(Math(data=f"n={n}", inline=True))
            doc.append(", our goal is to have ")
            doc.append(Math(data="r(\sigma) \cdot \delta(\sigma) \leq 2n^2 = " + str(2*(n**2)) + " \quad \\forall \sigma.", inline=True, escape=False))
            doc.append(LineBreak())
            
            doc.append(NoEscape(table(n)))
            doc.append(NewPage())

    doc.generate_tex(pdf_filename)
    print(f"tex file saved as {pdf_filename}.tex")






