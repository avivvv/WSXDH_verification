from latex.latex_document_generator import generate_tables_tex_for_range, generate_table_tex_for
from calculate.sp2n_data_supplier import create_sp2n_data__n_equals
import sys


if len(sys.argv) ==  2:
    generate_table_tex_for(int(sys.argv[1]))
else:
    generate_tables_tex_for_range(int(sys.argv[1]), int(sys.argv[2]))

