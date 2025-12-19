import pandas as pd
from sympy.combinatorics.partitions import IntegerPartition
from calculate.sp2n_calculator import delta, local_rates_at_peaks, b1, hypothesized_rate
import time


def create_sp2n_data__n_equals(n: int, printable_version: bool) -> pd.DataFrame:
    partitions = generate_all_partitions(n)
    data = generate_basic_data(partitions, n)

    return enrich_sp2n_data_for_printing(data, n) if printable_version else enrich_sp2n_data_for_verification(data, n)



def generate_all_partitions(n: int) -> list[dict[int, int]]:
    reg = IntegerPartition([2*n]);
    p = reg.copy()
    all_partitions = [];
    first_run = True;

    while p != reg or first_run:
        p_dict = p.as_dict();

        # The condition on partitions for sp_{2n} is that every odd part occurs with even multiplicity.
        if all([b % 2 == 0 for a,b in p_dict.items() if a % 2 == 1]):
            all_partitions.append(p_dict);
        
        p = p.prev_lex();
        first_run = False;
    
    return all_partitions;



def generate_basic_data(all_partitions: list[dict[int, int]], n: int) -> pd.DataFrame:
    data_set_length = len(all_partitions) - 2
    dataset = pd.DataFrame({
        'Partition': all_partitions[1:-1], # exclude the regular and trivial partitions.
        'Peaks': [None] * data_set_length,
        'max_indices': [None] * data_set_length,
        'local_rates_at_peaks': [None] * data_set_length,
        'Rate': [0.0] * data_set_length,
        'Delta': [0] * data_set_length,
        'r_delta': [0.0] * data_set_length
    })
    
    dataset['local_rates_at_peaks'] = dataset['Partition'].map(lambda partition: local_rates_at_peaks(partition, n))
    dataset['Rate'] = dataset['local_rates_at_peaks'].map(lambda local_rates: max(local_rates.values()))
    dataset['Delta'] = dataset['Partition'].map(delta)
    dataset['r_delta'] = dataset['Rate'] * dataset['Delta']
    dataset['Peaks'] = dataset['local_rates_at_peaks'].map(lambda local_rates: local_rates.keys())
    dataset['max_indices'] = dataset[['local_rates_at_peaks', 'Rate']].apply(indices_of_max_local_rate_DF_version, axis=1)
    
    return dataset


def enrich_sp2n_data_for_printing(dataset: pd.DataFrame, n: int):
    dataset = add_regular_and_trivial_partitions(dataset, n)
    dataset['Remarks'] = dataset['Partition'].map(lambda partition: get_remarks(partition, n))

    return dataset


def enrich_sp2n_data_for_verification(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    WSXDH_bound = 2*(n**2)
    dataset['WSXDH'] = dataset['r_delta'] <= WSXDH_bound

    prev_lex_rate = dataset['Rate'].shift(1, fill_value=float('inf'))
    dataset['rate_decreases'] = dataset['Rate'] <= prev_lex_rate # Hyp_1.4

    dataset['b_1'] = dataset['Partition'].map(b1)
    first_max = dataset['max_indices'].apply(lambda l: l[0] if l else 0)
    dataset['b1_maximizes_local_rate'] = dataset['b_1'] == first_max # Hyp_1.5 - extra sanity check

    dataset['hypothesized_rate'] = dataset['Partition'].map(lambda p: hypothesized_rate(p, n))
    dataset['Hyp_1.5'] = dataset['Rate'] == dataset['hypothesized_rate']

    dataset['Hyp_3.3.3_part1'] = dataset['local_rates_at_peaks'].map(lambda x: list(x.values())).map(lambda x: x == sorted(x, reverse=True))
    dataset['Hyp_3.3.3_part2'] = dataset[['Partition','max_indices']].apply(does_hypothesis_3_3_3_hold_DF_version, axis=1)

    return dataset


def add_regular_and_trivial_partitions(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    regular = [{(2*n): 1}, range(1, n+1), None, None, None, 0, None]
    trivial = [{1: 2*n}, [], range(1, n+1), None, 2, n**2, 2*(n**2)]

    dataset.loc[len(dataset)] = trivial
    dataset.index = dataset.index + 1
    dataset.loc[0] = regular

    return dataset.sort_index()


def indices_of_max_local_rate_DF_version(x):
    local_rates = x['local_rates_at_peaks']
    global_rate = x['Rate']

    return [i for i in local_rates.keys() if local_rates[i] == global_rate]


def does_hypothesis_3_3_3_hold_DF_version(x):
    parts = x['Partition'].keys()
    max_indices = x['max_indices']
 
    # The conditions after the 'or' are equivalent to the partition being either of
    # the type [a^b] or of the type [a^b, (a-1)^c].
    # In these cases the hypothesis does not apply, and thus we return True.
    return len(max_indices) == 1 or (len(parts) <= 2 and (max(parts) - min(parts) <= 1))


def get_remarks(partition: dict[int, int], n: int) -> str:
    if partition == {(2*n): 1}:
        return 'Principal'
    if partition == {1: 2*n}:
        return 'Trivial'
    if partition == {(2*n-2): 1, 2: 1}:
        return 'Subregular'
    if partition == {2: 1, 1: (2*n-2)}:
        return 'Minimal'
    
    if len(partition.keys()) == 1:
        return '$[a^b]$'
    
    if len(partition.keys()) == 2:
        if 1 in partition.keys() and 2 in partition.keys():
            return '$[2^b, 1^c]$'
        elif (max(partition.keys()) - min(partition.keys())) == 1:
            return '$[a^b, (a-1)^c]$'
        elif 1 in partition.keys():
            return '$[a^b, 1^c]$'
        
    return ''

