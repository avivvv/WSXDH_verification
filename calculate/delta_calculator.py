import calculate.partition_utils as utils


def delta(partition: list[(int,int)], n: int) -> int:
    utils.validate_partition(partition, n);

    p = utils.to_dict(partition).items();
    b_where_a_is_even = [b for a,b in p if a % 2 == 0];
    b_which_are_odd = [b for a,b in p if b % 2 == 1];
    sum_of_b_squared = sum([b**2 for a,b in p]);

    return (sum_of_b_squared / 4) + (len(b_which_are_odd) / 4) - (sum(b_where_a_is_even) / 2);