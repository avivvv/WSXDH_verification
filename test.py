from calculate.sp2n_data_supplier import generate_all_partitions, create_sp2n_data__n_equals
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


min_n = int(sys.argv[1])
max_n = int(sys.argv[2])

for n in range(min_n, max_n + 1):
    data = create_sp2n_data__n_equals(n)

    print(f"n={n}. SX holds:")
    sx = data['SX_holds'].all()
    print((bcolors.OKGREEN if sx else bcolors.FAIL) + str(sx) + bcolors.ENDC)

    print("rate is monotone:")
    mon = data['locally_monotone'].all()
    print((bcolors.OKGREEN if mon else bcolors.FAIL) + str(mon) + bcolors.ENDC)

    print("Was I right?")
    b1 = data['was_I_right'].all()
    print((bcolors.OKGREEN if b1 else bcolors.FAIL) + str(b1) + bcolors.ENDC)
