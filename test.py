from calculate.sp2n_data_supplier import create_sp2n_data__n_equals
import sys
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def assert_hypothesis(hypothesis_name: str):
    v = data[hypothesis_name].all()
    print(f"n={n}. {hypothesis_name} holds: {(bcolors.OKGREEN if v else bcolors.FAIL)}{str(v)}{bcolors.ENDC}")

    return v


min_n = int(sys.argv[1])
max_n = int(sys.argv[2])

assertions = {}
hypotheses_to_assert = ['WSXDH', 'rate_decreases', 'b1_maximizes_local_rate', 'Hyp_1.5', 'Hyp_3.3.3_part1', 'Hyp_3.3.3_part2']

for n in range(min_n, max_n + 1):
    start_time = time.perf_counter()
    data = create_sp2n_data__n_equals(n, printable_version=False)
    print(f"n={n}. Populating took: {(time.perf_counter() - start_time):.4f} seconds.")

    assertions[n] = [assert_hypothesis(hyp) for hyp in hypotheses_to_assert]    
    print(f"n={n}. Populating and asserting took: {(time.perf_counter() - start_time):.4f} seconds.")

print(f"{bcolors.BOLD}To summarize, for all n between {min_n} and {max_n}:{bcolors.ENDC}")

for hyp in hypotheses_to_assert:
    v = all([assertions[n][hyp] for n in range(min_n, max_n + 1)])
    print(f"{hyp} holds: {(bcolors.OKGREEN if v else bcolors.FAIL)}{str(v)}{bcolors.ENDC}")