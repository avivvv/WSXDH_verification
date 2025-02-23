import calculate.partition_utils as utils

    
def rate(partition: list[int], n: int) -> float:
    return rate_full_data(partition, n)['rate'];


def rate_full_data(partition: list[int], n: int) -> float:
    utils.validate_partition(partition, n);
    p = utils.to_list(partition);

    if p == [2*n]:
        raise ArithmeticError("the regular orbit is already known to have rate=infinity and should not be calculated in this method.")
    
    h_sums = sum_up(generate_H(p));
    full_data = {'h_sums': h_sums};
    full_data = calc_rate_from_h_sums(full_data, n);

    return full_data;


def generate_H(partition: list[int]) -> list[int]:
    diagonal = [];

    for d in partition:
        weights = list(range(-d+1, d+1, 2));
        diagonal.append(weights);

    diagonal = [h for sublist in diagonal for h in sublist];
    positive_diagonal = [h for h in diagonal if h > 0] + (int(diagonal.count(0)/2) * [0]);

    return sorted(positive_diagonal, reverse=True);


def calc_rate_from_h_sums(full_data: dict, n: int) -> dict:
    h_sums: list[int] = full_data['h_sums'];

    if len(h_sums) != n:
        raise ValueError(f"could not calculate rate. the number of h values in {h_sums} was not equal to n={n}.")

    fractions = [calc_fraction(h_sums, i, n) for i in range(1, n + 1)]
    max_value = max(fractions);
    max_index = fractions.index(max_value) + 1;
    
    full_data.update({'rate': 2 * max_value, 'max_index': max_index});
    return full_data;


def calc_fraction(h_sums: list[int], i: int, n: int) -> float:
    numerator = 2 * n * i - i ** 2;
    denominator = numerator - h_sums[i-1];

    if denominator == 0:
        raise ArithmeticError(f"could not calculate rate for h values {h_sums} because fractional value was infinity at i={i}.")
    
    return numerator / denominator;


def sum_up(arr: list[int]) -> list[int]:
    sums = [0];

    for x in arr:
        sums.append(sums[-1] + x);

    return sums[1:];