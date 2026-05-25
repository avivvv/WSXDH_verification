from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class Step(ABC):
    """A single stage in the verification pipeline."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, data: pd.DataFrame) -> pd.DataFrame: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class SourceStep(Step):
    """
    Generates the initial rows by calling fn(**kwargs).
    fn must return an iterable of objects to be stored in the specified column.
    Each kwarg (e.g. n=10) is stored as a column in every row of the data.
    """

    def __init__(self, column: str, fn, **kwargs):
        self._column = column
        self._fn = fn
        self._kwargs = kwargs


    @property
    def name(self) -> str:
        kw = ", ".join(f"{k}={v}" for k, v in self._kwargs.items())
        return f"source({self._fn.__name__}({kw}))"


    def run(self, _: pd.DataFrame) -> pd.DataFrame:
        data = self._fn(**self._kwargs)
        df = pd.DataFrame({self._column: list(data)})
        for k, v in self._kwargs.items():
            df[k] = v

        return df


class ComputeStep(Step):
    """
    Computes and adds a new column.
    fn receives a row (pd.Series) and returns the new value.
    If the function can be vectorized, set vectorized=True and fn will receive the whole DataFrame instead.

        .compute("func1", lambda row: func1(row["partition"]))
        .compute("product", lambda row: row["func1"] * row["func2"], vectorized=True)
    """

    def __init__(self, column: str, fn, source_col: str = None, vectorized: bool = False):
        self._column = column
        self._fn = fn
        self._source_col = source_col
        self._vectorized = vectorized


    @property
    def name(self) -> str:
        return f"compute({self._column!r})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        if self._vectorized:
            data[self._column] = self._fn(data)
        else:
            if self._source_col is not None:
                data[self._column] = data[self._source_col].map(self._fn)
            else:
                data[self._column] = data.apply(self._fn, axis=1)
        return data


class VerifyStep(Step):
    """
    Applies a boolean predicate to every row and stores the result in a new column.

    By default (raise_on_fail=False) the pipeline keeps running and
    the column records True/False.

        .verify("func1_bounded", lambda row: row["func1"] < x)
        .verify("known_family",  lambda row: ..., raise_on_fail=True)
    """

    def __init__(self, column: str, predicate, source_col: str = None, vectorized: bool = False, raise_on_fail: bool = False):
        self._column = column
        self._predicate = predicate
        self._source_col = source_col
        self._vectorized = vectorized
        self._raise_on_fail = raise_on_fail


    @property
    def name(self) -> str:
        suffix = ", raise_on_fail=True" if self._raise_on_fail else ""
        return f"verify({self._column!r}{suffix})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        if self._vectorized:
            results = self._predicate(data)
        else:
            if self._source_col is not None:
                results = data[self._source_col].map(self._predicate)
            else:
                results = data.apply(self._predicate, axis=1)

        data[self._column] = results.astype(bool)
        if self._raise_on_fail:
            failures = data[~results]
            if not failures.empty:
                raise VerificationError(self._column, failures.iloc[0])
            
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
            print("    (no rows to save)")
            return data
        
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(self._path, index=False)
        return data


class CustomStep(Step):
    """
    A custom step that can perform any arbitrary transformation on the DataFrame.

        .custom(lambda df: df[df["func1"] > x])
    """

    def __init__(self, name: str, fn):
        self._name = name
        self._fn = fn


    @property
    def name(self) -> str:
        return f"custom({self._name})"


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._fn(data)


class VerificationError(Exception):
    """Raised when a raise_on_fail verify step finds a counterexample."""

    def __init__(self, column: str, row: pd.Series):
        self.column = column
        self.row = row
        partition = row.get("partition", "?")
        super().__init__(
            f"Verification '{column}' failed on partition {partition}.\n"
            f"Full row: {row.to_dict()}"
        )
