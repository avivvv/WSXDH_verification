import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculate.sp2n_data_supplier import create_sp2n_data__n_equals
from pandas import DataFrame
import time


class color:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def to_string_color_coded(value: bool) -> str:
    color_code = color.GREEN if value else color.FAIL
    return f"{color_code}{str(value)}{color.ENDC}"


def verify_hypothesis(data: DataFrame, hypothesis_name: str):
    hypothesis_holds = data[hypothesis_name].all()
    print(f"n={n}. {hypothesis_name} holds: {to_string_color_coded(hypothesis_holds)}")

    return hypothesis_holds


min_n = int(sys.argv[1])
max_n = int(sys.argv[2])

verified_cases = {}
hypotheses_to_verify = ['Hyp_1.5', 'rate_monotone', 'WSXDH', 'b1_maximizes_local_rate', 'Hyp_3.3.3', 'Hyp_3.3.4']
for n in range(min_n, max_n + 1): # range is inclusive.
    # start_time = time.perf_counter()
    data = create_sp2n_data__n_equals(n, verify_conjectures=True)
    # created_data_time = time.perf_counter()
    # print(f"n={n}. Populating data took: {(created_data_time - start_time):.4f} seconds.")

    verified_cases[n] = {}
    for hypothesis_name in hypotheses_to_verify:
        hypothesis_holds = data[hypothesis_name].all()
        print(f"n={n}. {hypothesis_name} holds: {to_string_color_coded(hypothesis_holds)}")
        verified_cases[n][hypothesis_name] = hypothesis_holds

    # print(f"n={n}. Asserting hypotheses took: {(time.perf_counter() - created_data_time):.4f} seconds.")


print(f"{color.BOLD}To summarize, for all n between {min_n} and {max_n}:{color.ENDC}")
for hyp in hypotheses_to_verify:
    holds_for_all_n = all([verified_cases[n][hyp] for n in range(min_n, max_n + 1)])
    print(f"{hyp} holds: {to_string_color_coded(holds_for_all_n)}")