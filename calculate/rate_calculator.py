import calculate.partition_utils as utils

    
def rate(partition: list[int], n: int) -> float:
    return rate_full_data(partition, n)['rate'];


def h_value_sums(partition: list[int], n: int) -> list[int]:
    return rate_full_data(partition, n)['h_sums'];


def max_indices(partition: list[int], n: int) -> list[int]:
    return rate_full_data(partition, n)['max_indices'];


def rate_full_data(partition: list[int], n: int) -> float:
    utils.validate_partition(partition, n);
    p = utils.to_list(partition);

    if p == [2*n]:
        raise ArithmeticError("the regular orbit is already known to have rate=infinity and should not be calculated in this method.")
    
    h_sums = prefix_sums(generate_H(p, n));
    full_data = {'h_sums': h_sums};
    full_data = calc_rate_from_h_sums(full_data, n);

    return full_data;


def generate_H(partition: list[int], n: int) -> list[int]:
    all_weights = [];

    for d in partition:
        weights = list(range(-d+1, d+1, 2));
        all_weights.append(weights);

    # take the union of the lists
    diagonal = [h for sublist in all_weights for h in sublist];

    # take the first n highest values (these will be nonnegative)
    return sorted(diagonal, reverse=True)[:n];


def calc_rate_from_h_sums(full_data: dict, n: int) -> dict:
    h_sums: list[int] = full_data['h_sums'];

    if len(h_sums) != n:
        raise ValueError(f"could not calculate rate. the number of h values in {h_sums} was not equal to n={n}.")

    r_i_values = [];
    for i in range(1, n+1):
        r_i = 2/(1-(h_sums[i-1]/(2*n*i - i**2)))
        r_i_values.append(r_i);
    
    r = max(r_i_values);
    max_indices = [index for index in range(1, n+1) if r_i_values[index-1] == r];
    
    full_data.update({'rate': r, 'max_indices': max_indices});
    return full_data;


def prefix_sums(arr: list[int]) -> list[int]:
    sums = [0];

    for x in arr:
        sums.append(sums[-1] + x);

    return sums[1:];