from .partition_utils import a1, b1


# Compute δ of a partition according to the formula in Proposition 3.1.10.
def delta(partition: dict[int,int]) -> int:
    part_counts = partition.items()
    b_where_a_is_even = [b for a,b in part_counts if a % 2 == 0]
    b_which_are_odd = [b for a,b in part_counts if b % 2 == 1]
    sum_of_b_squared = sum([b**2 for a,b in part_counts])

    return int((sum_of_b_squared / 4) + (len(b_which_are_odd) / 4) - (sum(b_where_a_is_even) / 2))


# Compute the values on the diagonal of the dominant semisimple representative
# of the sl_2 triple assigned to the partition, according to Lemmas 3.2.5 and 3.2.8.
# It suffices to determine what is the value at each peak, since the diagonal is constant between consecutive peaks.
# For details about peaks see Definition 3.2.2.
# See also the original recipe for the diagonal values, Recipe 2.2.35.
# returns: a dictionary whose keys are the peak indices of the partition,
# and whose value at each peak p is h_p. 
def diagonal_values_at_peaks(partition: dict[int, int]) -> dict[int,int]:
    parts = partition.keys()
    even_parts = [a_j for a_j in parts if a_j % 2 == 0]
    odd_parts = [a_j for a_j in parts if a_j % 2 == 1]

    diagonal_values_by_peak = {}
    current_peak = 0

    # h is a possible value that can appear on the positive part of the diagonal.
    # Each part a_j of the partition that is larger than h can contribute an occurence of h
    # to the diagonal, if h=a_j-2*k+1 for some k, which happens when h and a_j are non-equal (mod 2).
    # The end of the range (h=0) is skipped, because it cannot correspond to any peak (n is a peak iff h_n!=0).
    for h in range(a1(partition)-1, 0, -1):
        parts_of_relevant_parity = odd_parts if h % 2 == 0 else even_parts
        # This is the set {a_j | a_j > h and a_j = h (mod 2)}, or in other words {a_j | j in J(h)}, from Lemma 3.2.5.
        # Namely these are all the parts which contribute h to the diagonal.
        parts_in_J_of_h = [a_j for a_j in parts_of_relevant_parity if a_j > h]

        if len(parts_in_J_of_h) == 0:
            continue
        
        multiplicity_sum = sum([partition[a_j] for a_j in parts_in_J_of_h])
        current_peak += multiplicity_sum
        diagonal_values_by_peak[current_peak] = h
    
    return diagonal_values_by_peak


# Compute the local rate r_i at each peak index i of the partition, according to Definition 3.2.1.
# returns: a dictionary whose keys are the peak indices of the partition,
# and whose values are the local rates at each peak. 
def local_rates_at_peaks(partition: dict[int, int], n: int) -> dict[int,float]:
    diagonal_values_by_peak = diagonal_values_at_peaks(partition)
    peaks = sorted(diagonal_values_by_peak.keys())
    previous_peak = 0
    sum_of_h_k = 0
    local_rates_by_peak = {}

    for p in peaks:
        h_p = diagonal_values_by_peak[p]
        sum_of_h_k += (p - previous_peak) * h_p
        numerator = 4*n*p - 2*(p**2)
        denominator = 2*n*p - p**2 - sum_of_h_k
        local_rates_by_peak[p] = numerator / denominator
        previous_peak = p

    return local_rates_by_peak
    

# This predicate tests whether the partition satisfies Hypothesis 3.3.4.
def verify_hypothesis_3_3_4(parts: list[int], local_rates_by_peak: dict[int, float], b_1: int, rate: float) -> bool:
    # These conditions are equivalent to the partition being either of
    # the type [a^b] or of the type [a^b, (a-1)^c].
    # In these cases the hypothesis does not apply, and thus we return True.
    if len(parts) <= 2 and (max(parts) - min(parts) <= 1):
        return True

    return all(i == b_1 or r_i < rate for i,r_i in local_rates_by_peak.items())


def indices_of_max_local_rate(local_rates_by_peak: dict[int, float], rate: float) -> list[int]:
    return [i for i,r_i in local_rates_by_peak.items() if r_i == rate]


# This function computes the value of the formula in Hypothesis 1.5.
# If Hypothesis 1.5 holds for the partition at hand, the returned value of this function
# should be equal to the actual rate of the partition
def hypothesized_rate(a_1: int, b_1: int, n: int) -> float:
    return (4*n - 2*b_1) / (2*n - a_1 - b_1 + 1)