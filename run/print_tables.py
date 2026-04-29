import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from latex.latex_document_generator import generate_tables_tex_for_range, generate_table_tex_for


if len(sys.argv) ==  2:
    generate_table_tex_for(int(sys.argv[1]))
else:
    generate_tables_tex_for_range(int(sys.argv[1]), int(sys.argv[2]))
