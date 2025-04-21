from latex.latex_document_generator import generate_tables_pdf_for_range as create_pdf
from calculate.sp2n_data_supplier import create_sp2n_data__n_equals
import pandas as pd

# print("enter n")
# print(create_sp2n_data__n_equals(int(input())))
for n in range(38,50):
    data = create_sp2n_data__n_equals(n)
    print(f"n={n}.")
    print(data['SX_holds'].all())