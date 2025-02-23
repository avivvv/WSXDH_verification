from calculate.sp2n_data_supplier import generate_all_partitions, create_sp2n_data__n_equals
import sys
import time
import numpy as np

n = int(sys.argv[1])

start = time.perf_counter()
print(len(generate_all_partitions(n)))
print(time.perf_counter() - start)

start2 = time.perf_counter()
data = create_sp2n_data__n_equals(n)
print(f"n={n}.")
print(np.all(data['SX_holds']))
print(time.perf_counter() - start2)
