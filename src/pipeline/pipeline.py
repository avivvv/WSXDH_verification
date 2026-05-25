from __future__ import annotations
import pandas as pd
from .step import CustomStep, Step, SourceStep, ComputeStep, VerifyStep, SaveStep


class Pipeline:
    def __init__(self, steps: list[Step]):
        self._steps = steps


    def run(self) -> pd.DataFrame:
        data: pd.DataFrame = pd.DataFrame()
        counter_width = len(str(len(self._steps)))

        for i, step in enumerate(self._steps, 1):
            label = f"[{i:{counter_width}}/{len(self._steps)}]"
            print(f"  {label} {step.name} ...", end=" ", flush=True)
            data = step.run(data)
            print(data)

        return data


    def __repr__(self) -> str:
        step_lines = "\n  ".join(repr(s) for s in self._steps)
        return f"Pipeline(\n  {step_lines}\n)"


class PipelineBuilder:
    """
    Builder class for Pipeline.
    Steps are appended in call order and executed in that same order
    when Pipeline.run() is called.
    """

    def __init__(self):
        self._steps: list[Step] = []
        self._source_col = None


    def source(self, column: str, fn, **kwargs) -> PipelineBuilder:
        self._steps.append(SourceStep(column, fn, **kwargs))
        self._source_col = column
        return self


    def compute(self, column: str, fn, source_col: str = None, vectorized: bool = False) -> PipelineBuilder:
        if source_col is None:
            source_col = self._source_col

        self._steps.append(ComputeStep(column, fn, source_col, vectorized))
        return self


    def verify(
        self,
        column: str,
        predicate,
        source_col: str = None,
        vectorized: bool = False,
        raise_on_fail: bool = False,
    ) -> PipelineBuilder:
        if source_col is None:
            source_col = self._source_col
            
        self._steps.append(VerifyStep(column, predicate, source_col, vectorized, raise_on_fail))
        return self


    def save(self, path: str) -> PipelineBuilder:
        self._steps.append(SaveStep(path))
        return self
    

    def custom(self, name: str, fn) -> PipelineBuilder:
        self._steps.append(CustomStep(name, fn))
        return self


    def build(self) -> Pipeline:
        self._validate()
        return Pipeline(list(self._steps))


    def _validate(self) -> None:
        if not self._steps:
            raise PipelineError("Pipeline has no steps.")
        if not isinstance(self._steps[0], SourceStep):
            raise PipelineError("First step must be .source(...).")
        if not isinstance(self._steps[-1], SaveStep):
            raise PipelineError("Last step must be .save(...).")
        sources = [s for s in self._steps if isinstance(s, SourceStep)]
        if len(sources) > 1:
            raise PipelineError("Pipeline may only have one .source(...).")


    def __repr__(self) -> str:
        step_lines = "\n  ".join(repr(s) for s in self._steps)
        return f"PipelineBuilder(\n  {step_lines}\n)"


class PipelineError(Exception):
    """Custom exception for pipeline validation errors."""
