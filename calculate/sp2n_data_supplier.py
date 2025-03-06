import numpy as np
from sympy.combinatorics.partitions import IntegerPartition
from calculate.rate_calculator import rate
from calculate.delta_calculator import delta
# from sage.all import *


def generate_all_partitions(n: int) -> list[dict[int, int]]:
    reg = IntegerPartition([2*n]);
    p = reg.copy()
    all_partitions = [];
    first_run = True;

    while p != reg or first_run:
        p_dict = p.as_dict();

        # the condition on partitions for sp_{2n} is that every odd part occurs with even multiplicity.
        if all([b % 2 == 0 for a,b in p_dict.items() if a % 2 == 1]):
            all_partitions.append(p_dict);
        
        p = p.prev_lex();
        first_run = False;
    
    return all_partitions;



def create_sp2n_data__n_equals(n: int):
    all_partitions = generate_all_partitions(n)

    dtype = [('Partition', 'O'), ('rate_full_data', 'O'), ('h_value_sums', 'O'), ('index_of_rate', 'i2'), ('Rate', 'f8'), ('Delta', 'i8'), ('r*delta', 'f8'), ('SX_holds', '?')]
    dataset = np.zeros(len(all_partitions)-1, dtype=dtype)

    dataset['Partition'] = all_partitions[1:] # exclude the regular orbit

    fast_rate = np.vectorize(lambda partition: rate(partition, n))
    # extract_rate = np.vectorize(lambda data: data['rate'])
    # extract_h_sums = np.vectorize(lambda data: data['h_sums'])
    # extract_max_index = np.vectorize(lambda data: data['max_index'])
    fast_delta = np.vectorize(lambda partition: delta(partition, n))

    # dataset['rate_full_data'] = fast_rate_full_data(dataset['Partition'])
    # dataset['h_value_sums'] = extract_h_sums(dataset['rate_full_data'])
    # dataset['index_of_rate'] = extract_max_index(dataset['rate_full_data'])
    dataset['Rate'] = fast_rate(dataset['Partition'])
    dataset['Delta'] = fast_delta(dataset['Partition'])
    dataset['r*delta'] = dataset['Rate'] * dataset['Delta']

    SX_goal = 2*(n**2)
    constant_value_column = np.array((len(all_partitions)-1) * [SX_goal])
    dataset['SX_holds'] = np.less_equal(dataset['r*delta'], constant_value_column)

    # readd regular orbit:
    # dataset = np.vstack(["insert regular orbit here", dataset])

    return dataset

