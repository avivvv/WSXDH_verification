import pandas as pd
from sympy.combinatorics.partitions import IntegerPartition
from calculate.partition_utils import a1, b1
from .sp2n_calculator import delta, local_rates_at_peaks, hypothesized_rate, indices_of_max_local_rate, verify_hypothesis_3_3_4
import time


def create_sp2n_data__n_equals(n: int, verify_conjectures: bool = False, printable_version: bool = False) -> pd.DataFrame:
    partitions = generate_all_partitions(n)
    data = generate_basic_data(partitions, n)

    if verify_conjectures:
        return enrich_sp2n_data_for_verification(data, n)
    
    if printable_version:
        return enrich_sp2n_data_for_printing(data, n)



def generate_all_partitions(n: int) -> list[dict[int, int]]:
    reg = IntegerPartition([2*n])
    p = reg.copy()
    all_partitions = []
    first_run = True

    while p != reg or first_run:
        partition = p.as_dict()

        # The condition on partitions for sp2n is that every odd part occurs with even multiplicity.
        if all([b % 2 == 0 for a,b in partition.items() if a % 2 == 1]):
            all_partitions.append(partition)
        
        p = p.prev_lex()
        first_run = False
    
    return all_partitions



def generate_basic_data(all_partitions: list[dict[int, int]], n: int) -> pd.DataFrame:
    partitions = all_partitions[1:-1]  # exclude the regular and trivial partitions.
    dataset = pd.DataFrame({
        'Partition': partitions,
        'a_1': [a1(partition) for partition in partitions],
        'b_1': [b1(partition) for partition in partitions]
    })
    
    dataset['local_rates_at_peaks'] = dataset['Partition'].map(lambda partition: local_rates_at_peaks(partition, n))
    dataset['Rate'] = dataset['local_rates_at_peaks'].map(lambda local_rates: max(local_rates.values()))
    dataset['Delta'] = dataset['Partition'].map(delta)
    dataset['r_delta'] = dataset['Rate'] * dataset['Delta']
    dataset['max_indices'] = [
        indices_of_max_local_rate(local_rates_by_peak, rate)
        for local_rates_by_peak, rate in zip(dataset['local_rates_at_peaks'], dataset['Rate'])
    ]
    
    return dataset


def enrich_sp2n_data_for_printing(dataset: pd.DataFrame, n: int):
    dataset['Peaks'] = dataset['local_rates_at_peaks'].map(lambda local_rates_by_peak: local_rates_by_peak.keys())
    dataset = add_regular_and_trivial_partitions(dataset, n)
    dataset['Remarks'] = dataset['Partition'].map(lambda partition: get_remarks(partition, n))

    return dataset


def enrich_sp2n_data_for_verification(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    # Since hypothesized_rate only performs arithmetic, we can vectorize it.
    dataset['hypothesized_rate'] = hypothesized_rate(dataset['a_1'], dataset['b_1'], n)
    dataset['Hyp_1.5'] = dataset['Rate'] == dataset['hypothesized_rate'] # Hypothesis 1.5 - main conjecture.

    prev_lex_rate = dataset['Rate'].shift(1, fill_value=float('inf'))
    dataset['rate_monotone'] = dataset['Rate'] <= prev_lex_rate # Hypothesis 1.4.

    WSXDH_bound = 2*(n**2)
    dataset['WSXDH'] = dataset['r_delta'] <= WSXDH_bound # Hypothesis 1.3.

    first_max = dataset['max_indices'].apply(lambda l: l[0] if l else 0)
    dataset['b1_maximizes_local_rate'] = dataset['b_1'] == first_max # Independent verification for Hypothesis 1.5.

    # Hypothesis 3.3.3 - Check descending order of local rate values.
    dataset['Hyp_3.3.3'] = dataset['local_rates_at_peaks'].map(
        lambda d: all(r_i >= r_j for r_i, r_j in zip(d.values(), list(d.values())[1:]))
    )

    # Hypothesis 3.3.4 - Check that max local rate is obtained uniquely at b_1, excluding certain partition families.
    dataset['Hyp_3.3.4'] = [
        verify_hypothesis_3_3_4(partition.keys(), local_rates_by_peak, b_1, rate)
        for partition, local_rates_by_peak, b_1, rate in zip(
            dataset['Partition'],
            dataset['local_rates_at_peaks'],
            dataset['b_1'],
            dataset['Rate']
        )
    ]

    return dataset


def add_regular_and_trivial_partitions(dataset: pd.DataFrame, n: int) -> pd.DataFrame:
    cols = dataset.columns.tolist()
    # Columns: Partition, a_1, b_1, local_rates_at_peaks, Rate, Delta, r_delta, max_indices, Peaks
    regular_vals = [{(2*n): 1}, range(1, n+1), None, None, None, 0, None, None, range(1, n+1)]
    trivial_vals = [{1: 2*n}, [], range(1, n+1), None, 2, n**2, 2*(n**2), range(1, n+1), []]

    regular_row = pd.DataFrame([dict(zip(cols, regular_vals))])
    trivial_row = pd.DataFrame([dict(zip(cols, trivial_vals))])

    return pd.concat([regular_row, dataset, trivial_row], ignore_index=True)


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