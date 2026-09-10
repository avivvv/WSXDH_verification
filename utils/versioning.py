from datetime import datetime

def get_results_file_name(n: int):
    return f"results/sp{2*n}.csv"


def get_latex_file_name(min_n: int, max_n: int):
    """
    Returns a file name *without an extention*,
    to serve both as the name of a ``TeX`` file and a ``pdf`` file
    """
    today_str = datetime.today().date().isoformat()
    return f"results/latex/{today_str}/sp{2*min_n}-sp{2*max_n}"