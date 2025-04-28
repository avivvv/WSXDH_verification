from latex.latex_document_generator import generate_tables_pdf_for_range as create_pdf
import sys

create_pdf(int(sys.argv[1]), int(sys.argv[2]));
