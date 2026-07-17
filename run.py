import sys
from core.sp2n_pipeline import sp2n_pipeline
from latex.latex_table_generator import generate_tex_doc
from utils.versioning import get_results_file_name
from utils.styles import color, console


def generate_sp2n_dataset_for_single_n(n: int):
    console.set_window_title(f"sp2n Dataset Generation (n = {n})")
    console.print(f"Generating sp2n dataset for n = {n}.")

    save_path = get_results_file_name(n)
    sp2n_pipeline(n, save_path).run()


def generate_tex_doc_for_range(min_n: int, max_n: int):      
    console.set_window_title(f"sp2n LaTeX Document Generation ({min_n} <= n <= {max_n})")
    console.print(f"Generating LaTeX tables for sp2n datasets from n = {min_n} up to n = {max_n}.")

    generate_tex_doc(min_n, max_n)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        n = int(sys.argv[1])
        generate_sp2n_dataset_for_single_n(n)
    elif len(sys.argv) == 3:
        min_n = int(sys.argv[1])
        max_n = int(sys.argv[2])
        generate_tex_doc_for_range(min_n, max_n)
    else:
        console.print_exception(ValueError("Wrong number of arguments passed."))
        console.print(f"Usage: {color("python run.py <n>", "blue")} or {color("python run.py <min_n> <max_n>", "blue")}")
        sys.exit(1)
