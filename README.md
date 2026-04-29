# Verification of the Weak Sarnak-Xue Density Hypothesis

This project contains a computer verification of the Weak Sarnak-Xue Density Hypothesis for $SO_{2n+1}(\mathbb R)$,
as posed in the work of author Aviv Hendler as part of his Master's Thesis in Mathematics at the Hebrew University of Jerusalem,
under the supervision of Dr. Shai Evra.


### How to run this code:
There are two possible entry points to this project - `verify_conjectures.py` and `print_tables.py` (see below). Both entry points accept two integers parameters representing a range (inclusive) of values for the rank (n) of the groups SO_{2n+1}.
For example:
```
python verify_conjectures.py 2 50
```
will verify that all conjectures from the paper hold for all the partitions in all of the groups SO_{2n+1}, where 2 <= n <= 50.

### Outcome of each entry point:
1. By running `verify_conjectures.py`, the code will verify that all of the conjectures made in the paper. For each n in the given range, it will check that each of the conjectures hold, and will output the results to `stdout`.
2. By running `print_tables.py`, the code will generate a `.tex` file containing formatted tables with the calculated data of all partitions, for each n in the given range.
