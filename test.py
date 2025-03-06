from calculate.sp2n_data_supplier import generate_all_partitions, create_sp2n_data__n_equals
import sys
import time
import numpy as np


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


max_n = int(sys.argv[1])

for n in range(2, max_n + 1):
    # start = time.perf_counter()
    # print(len(generate_all_partitions(n)))
    # print(time.perf_counter() - start)

    start2 = time.perf_counter()
    data = create_sp2n_data__n_equals(n)
    print(f"n={n}. SX holds:")
    sx = np.all(data['SX_holds'])
    print((bcolors.OKGREEN if sx else bcolors.FAIL) + str(sx) + bcolors.ENDC)

    prev_lex_rate = [float('inf')]
    prev_lex_rate.extend(data['Rate'])
    prev_lex_rate = prev_lex_rate[:-1]

    print("rate is monotone:")
    mon = np.all(np.less_equal(data['Rate'], prev_lex_rate))
    print((bcolors.OKGREEN if mon else bcolors.FAIL) + str(mon) + bcolors.ENDC)
    # print(time.perf_counter() - start2)
