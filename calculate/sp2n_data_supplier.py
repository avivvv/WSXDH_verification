import pandas as pd
from sympy.combinatorics.partitions import IntegerPartition
from calculate.rate_calculator import rate, h_value_sums, max_indices
from calculate.delta_calculator import delta
from calculate.partition_utils import b1


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
    all_partitions = generate_all_partitions(n)[1:-1] # exclude the regular and trivial partitions.
    dataset = pd.DataFrame({
        'Partition': all_partitions,
        'h_value_sums': [None] * (len(all_partitions)),
        'max_indices': [None] * (len(all_partitions)),
        'Rate': [0.0] * (len(all_partitions)),
        'Delta': [0] * (len(all_partitions)),
        'r_delta': [0.0] * (len(all_partitions)),
        'SX_holds': [False] * (len(all_partitions)),
        'locally_monotone': [False] * (len(all_partitions)),
        'was_I_right': [False] * (len(all_partitions))
    })
    
    dataset['Rate'] = dataset['Partition'].apply(lambda partition: rate(partition, n))
    dataset['Delta'] = dataset['Partition'].apply(lambda partition: delta(partition, n))
    dataset['r_delta'] = dataset['Rate'] * dataset['Delta']

    dataset['h_value_sums'] = dataset['Partition'].apply(lambda partition: h_value_sums(partition, n))
    dataset['max_indices'] = dataset['Partition'].apply(lambda partition: max_indices(partition, n))

    dataset['SX_holds'] = dataset['r_delta'] <= 2*(n**2)

    prev_lex_rate = dataset['Rate'].shift(1, fill_value=float('inf'))
    dataset['locally_monotone'] = dataset['Rate'] <= prev_lex_rate

    b1_of_partition = dataset['Partition'].apply(b1)
    first_max = dataset['max_indices'].apply(lambda l: l[0])
    dataset['was_I_right'] = b1_of_partition == first_max

    return dataset

