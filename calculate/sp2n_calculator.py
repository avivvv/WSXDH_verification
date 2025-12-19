from calculate.partition_utils import a1, b1, tostring
   

# Compute δ of a partition according to the formula in Proposition 3.1.10 (TODO: review references)
def delta(partition: dict[int,int]) -> int:
    p = partition.items();
    b_where_a_is_even = [b for a,b in p if a % 2 == 0];
    b_which_are_odd = [b for a,b in p if b % 2 == 1];
    sum_of_b_squared = sum([b**2 for a,b in p]);

    return int((sum_of_b_squared / 4) + (len(b_which_are_odd) / 4) - (sum(b_where_a_is_even) / 2));


# Compute the rate of a partition of 2n according to the formula in Definition 3.2.1 (TODO: review references)
def rate(partition: dict[int, int], n: int) -> float:
    return max(local_rates_at_peaks(partition, n));


# This predicate tests whether the partition satisfies Hypothesis 1.5 (TODO: review references)
def is_local_rate_maximized_at_b1(partition: dict[int, int], n: int) -> bool:
    local_rates_at_peaks = local_rates_at_peaks(partition, n);
    
    return max(local_rates_at_peaks.values()) == local_rates_at_peaks[b1(partition)];


# This predicate tests whether the partition satisfies Hypothesis 3.3.3 (TODO: review references)
def does_hypothesis_3_3_3_hold(partition: dict[int, int], n: int) -> bool:
    parts = partition.keys();

    # These conditions are equivalent to the partition being either of
    # the type [a^b] or of the type [a^b, (a-1)^c].
    # In these cases the hypothesis does not apply, and thus we return True.
    if len(parts) <= 2 and (max(parts) - min(parts) <= 1):
        return True;

    return is_max_at_b1_unique(partition, n);


def is_max_at_b1_unique(partition: dict[int, int], n: int) -> bool:
    local_rates_at_peaks = local_rates_at_peaks(partition, n);
    b_1 = b1(partition)
    r_b_1 = local_rates_at_peaks[b_1];

    local_rates_except_at_b1 = local_rates_at_peaks.copy();
    del local_rates_except_at_b1[b_1];

    return all(r_i < r_b_1 for r_i in local_rates_except_at_b1.values());


def indices_of_max_local_rate(partition: dict[int, int], n: int) -> list[int]:
    local_rates_at_peaks = local_rates_at_peaks(partition, n);
    rate = max(local_rates_at_peaks.values())

    return [i for i in local_rates_at_peaks.keys() if local_rates_at_peaks[i] == rate]


# This predicate tests whether the partition satisfies Hypothesis ?? (TODO: review references) 
def are_local_rates_at_peaks_descending(partition: dict[int, int], n: int) -> bool:
    local_rates_at_peaks = local_rates_at_peaks(partition, n);
    peaks = local_rates_at_peaks.keys();
    local_rates_at_peaks_sorted_by_index = [];

    for i in sorted(peaks, reverse=True):
        local_rates_at_peaks_sorted_by_index.append(local_rates_at_peaks[i]);
    
    return local_rates_at_peaks_sorted_by_index == sorted(local_rates_at_peaks_sorted_by_index);


# Compute the values on the diagonal of the dominant semisimple representative
# of the sl_2 triple assigned to the partition, according to Recipe 2.2.35 (TODO: review references).
# It suffices to determine what is the value at each peak, since the diagonal is constant between adjacent peaks.
# For details about peaks see Definition 3.2.2 (TODO: review references).
# See also Proposition 3.2.4 and its proof (TODO: review references).
# returns: a dictionary whose keys are the peak indices of the partition,
# and whose value at each peak p is h_p. 
def diagonal_values_at_each_peak(partition: dict[int, int]) -> dict[int,int]:
    parts = partition.keys();
    even_parts = [d for d in parts if d % 2 == 0];
    odd_parts = [d for d in parts if d % 2 == 1];

    diagonal_values_at_peaks = {};
    current_peak = 0;

    # h is a possible value that can appear on positive part of the diagonal.
    # Each part a_i of the partition that is larger than h can contribute
    # an occurence of h to the diagonal, if h=a_i-2*k+1 for some k.
    # The end of the range (h=0) is skipped, because it cannot correspond to any peak (n is a peak iff h_n!=0).
    for h in range(a1(partition)-1, 0, -1):
        parts_with_relevant_parity = odd_parts if h % 2 == 0 else even_parts;
        parts_which_contribute_h_to_diagonal = [d for d in parts_with_relevant_parity if d > h];

        if len(parts_which_contribute_h_to_diagonal) == 0:
            continue;
        
        sum_of_multiplicities = sum([partition[d] for d in parts_which_contribute_h_to_diagonal]);
        current_peak += sum_of_multiplicities;
        diagonal_values_at_peaks[current_peak] = h;
    
    return diagonal_values_at_peaks;


# Compute the local rate r_i at each peak index i of the partition, according to Definition 3.2.1 (TODO: review references).
# returns: a dictionary whose keys are the peak indices of the partition,
# and whose values are the local rates at each peak. 
def local_rates_at_peaks(partition: dict[int, int], n: int) -> dict[int,float]:
    diagonal_values_at_peaks = diagonal_values_at_each_peak(partition);
    peaks = sorted(diagonal_values_at_peaks.keys());
    previous_peak = 0;
    sum_of_h_k = 0;
    local_rates_at_peaks = {};

    for i in peaks:
        sum_of_principal_diagonal = 2*n*i - i**2;
        h_i = diagonal_values_at_peaks[i];
        sum_of_h_k += (i - previous_peak) * h_i;
        r_i = 2 * sum_of_principal_diagonal / (sum_of_principal_diagonal - sum_of_h_k);
        local_rates_at_peaks[i] = r_i;
        previous_peak = i;

    return local_rates_at_peaks;
    

# This function computes the value of the formula in Hypothesis 1.5 (TODO: review references).
# If Hypothesis 1.5 holds for the partition at hand, the returned value of this function
# should be equal to the actual rate of the partition
def hypothesized_rate(partition: dict[int, int], n: int) -> float:
    a_1 = a1(partition);
    b_1 = b1(partition);

    return (4*n - 2*b_1) / (2*n - a_1 - b_1 + 1);