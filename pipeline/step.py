from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

from utils.styles import console, bold, status_as_text


class Step(ABC):
    """A single stage in the verification pipeline."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, data: pd.DataFrame) -> pd.DataFrame: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class CreateStep(Step):
    """
    Generates the initial data by calling fn(**kwargs).
    fn must return an iterable of objects (e.g. partitions) to be stored in the specified column.
    Each kwarg (e.g. n=10) is stored as a column in every row of the data.
    """

    def __init__(self, fn, column: str = "Partition", **kwargs):
        self._fn = fn
        self._column = column
        self._kwargs = kwargs


    @property
    def name(self) -> str:
        kw = ", ".join(f"{k}={v}" for k, v in self._kwargs.items())
        return f"create({self._fn.__name__}({kw}))"


    def run(self, _: pd.DataFrame) -> pd.DataFrame:
        data = self._fn(**self._kwargs)
        df = pd.DataFrame({self._column: list(data)})
        
        for k, v in self._kwargs.items():
            df[k] = v

        print(f"Created dataset with {len(data)} partitions using {self._fn.__name__} with {self._kwargs}.")

        return df


class ComputeStep(Step):
    """
    Computes and adds a new column.
    fn receives a row (pd.Series) and returns the new value.
    If the function can be vectorized, set vectorized=True and fn will receive the whole DataFrame instead.
    If the function depends on specific columns, list them in source_cols,
    and fn will receive the values of those columns as arguments instead of the whole row.

        .compute("func1", lambda row: func1(row["partition"]))
        .compute("product", lambda df: df["val1"] * df["val2"], vectorized=True)
    """

    def __init__(self, result_col: str, fn, source_cols: list[str] = None, vectorized: bool = False):
        self._result_col = result_col
        self._fn = fn
        self._source_cols = source_cols
        self._vectorized = vectorized


    @property
    def name(self) -> str:
        return f"compute({self._result_col!r})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute the new column and add it to the DataFrame.
        Multiple methods are supported to achieve the best performance based on the function's characteristics.
        """
        fn = self._fn

        if self._vectorized:
            result = fn(data)
        elif self._source_cols and len(self._source_cols) == 1:
            result = data[self._source_cols[0]].map(fn)
        elif self._source_cols and len(self._source_cols) > 1:
            result = [fn(*values) for values in zip(*(data[col] for col in self._source_cols))]
        else:
            result = data.apply(fn, axis=1)
        
        data[self._result_col] = result
        return data


class VerifyStep(Step):
    """
    Applies a boolean predicate to every row and stores the result in a new column.
    Prints total counts of True/False.

    By default (raise_on_fail=False) the pipeline keeps running and
    the column records True/False.

        .verify("func1_bounded", lambda row: row["func1"] < x)
        .verify("belongs_to_known_family",  lambda row: ..., raise_on_fail=True)
    """

    def __init__(self, result_col: str, predicate, source_col: str = None, vectorized: bool = False, raise_on_fail: bool = False):
        self._result_col = result_col
        self._predicate = predicate
        self._source_col = source_col
        self._vectorized = vectorized
        self._raise_on_fail = raise_on_fail


    @property
    def name(self) -> str:
        suffix = ", raise_on_fail=True" if self._raise_on_fail else ""
        return f"verify({self._result_col!r}{suffix})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        if self._vectorized:
            results = self._predicate(data)
        elif self._source_col:
            results = data[self._source_col].map(self._predicate)
        else:
            results = data.apply(self._predicate, axis=1)

        self.print_summary(results)
        self.raise_if_necessary(data, results)

        data[self._result_col] = results.astype(bool)
        return data
    

    def print_summary(self, results):
        total = len(results)
        passed = results.sum()
        console.print(f"        {bold(self._result_col)}:   {status_as_text[all(results)]}")
        console.print(f"        {passed}/{total} partitions passed.")


    def raise_if_necessary(self, data, results):
        if self._raise_on_fail:
            failures = data[~results]
            if not failures.empty:
                raise VerificationError(self._result_col, failures.iloc[0])


class LoadStep(Step):
    """
    Loads data from a CSV file.

        .load("data/partitions_n10.csv")
    """

    def __init__(self, path: str):
        self._path = Path(path)


    @property
    def name(self) -> str:
        return f"load({self._path})"


    def run(self) -> pd.DataFrame:
        data = pd.read_csv(self._path)
        console.print(f"    Loaded dataset with {len(data)} partitions from {self._path}")
        return data


class SaveStep(Step):
    """
    Writes all rows to a CSV file.
    The parent directory is created if it does not exist.

        .save("data/partitions_n10.csv")
    """

    def __init__(self, path: str):
        self._path = Path(path)


    @property
    def name(self) -> str:
        return f"save({self._path})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            console.print("    (no rows to save)")
            return data
        
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(self._path, index=False)
        console.print(f"    Saved {len(data)} rows to {self._path}")
        return data


class CustomStep(Step):
    """
    A custom step that can perform any arbitrary transformation on the DataFrame by calling fn(data, **kwargs).
    fn must return the new dataframe to be passed on to the next steps.

        .then(lambda df: df[df["func1"] > x])
    """

    def __init__(self, fn, **kwargs):
        self._fn = fn
        self._kwargs = kwargs


    @property
    def name(self) -> str:
        kw = ", ".join(f"{k}={v}" for k, v in self._kwargs.items())
        return f"custom({self._fn.__name__}({kw}))"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._fn(data, **self._kwargs)


class VerificationError(Exception):
    """Raised when a raise_on_fail verify step finds a counterexample."""

    def __init__(self, column: str, row: pd.Series):
        self.column = column
        self.row = row
        partition = row.get("partition", "?")
        super().__init__(
            f"Verification of '{column}' failed on partition {partition}.\n"
            f"Full row: {row.to_dict()}"
        )
