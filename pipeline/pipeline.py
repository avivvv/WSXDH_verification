from __future__ import annotations
import pandas as pd
from collections.abc import Iterable

from utils.styles import console, Indicators
from .step import CustomStep, LoadStep, Step, CreateStep, ComputeStep, VerifyStep, SaveStep


class Pipeline:
    def __init__(self, steps: list[Step]):
        self._steps = steps


    def run(self, verbose=False) -> pd.DataFrame:
        console.print(f"Running pipeline ({len(self._steps)} steps).")

        data: pd.DataFrame = pd.DataFrame()
        counter_width = len(str(len(self._steps)))

        for i, step in enumerate(self._steps, 1):
            if verbose:
                step_number = f"[{i:{counter_width}}/{len(self._steps)}]"
                console.print(f"  {step_number} {step.name}.")
            data = step.run(data)

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

    
    @classmethod
    def expand(pipeline: Pipeline) -> PipelineBuilder:
        """Create a PipelineBuilder from an existing Pipeline, allowing further steps to be added."""
        builder = PipelineBuilder()
        builder._steps = list(pipeline._steps)
        return builder


    def create(self, fn: callable[Iterable], column: str = "Partition", **kwargs) -> PipelineBuilder:
        self._steps.append(CreateStep(fn, column, **kwargs))
        return self


    def compute(self, result_col: str, fn: callable, source_cols: list[str] = None, vectorized: bool = False) -> PipelineBuilder:
        self._steps.append(ComputeStep(result_col, fn, source_cols, vectorized))
        return self


    def verify(
        self,
        result_col: str,
        predicate: callable[bool],
        source_col: str = None,
        vectorized: bool = False,
        raise_on_fail: bool = False,
    ) -> PipelineBuilder:            
        self._steps.append(VerifyStep(result_col, predicate, source_col, vectorized, raise_on_fail))
        return self


    def load(self, path: str) -> PipelineBuilder:
        self._steps.append(LoadStep(path))
        return self
    

    def save(self, path: str) -> PipelineBuilder:
        self._steps.append(SaveStep(path))
        return self
    

    def then(self, fn: callable[pd.DataFrame], **kwargs) -> PipelineBuilder:
        self._steps.append(CustomStep(fn, **kwargs))
        return self


    def build_pipeline(self) -> Pipeline:
        self._validate_steps()
        return Pipeline(list(self._steps))


    def _validate_steps(self) -> None:
        if not self._steps:
            raise PipelineError("Pipeline has no steps.")
        if not isinstance(self._steps[0], (CreateStep, LoadStep)):
            raise PipelineError("First step must be .create(...) or .load(...).")
        if not any(isinstance(s, SaveStep) for s in self._steps):
            raise PipelineError("Pipeline must have at least one .save(...) step.")
        if len([s for s in self._steps if isinstance(s, (CreateStep, LoadStep))]) > 1:
            console.print(
                Indicators.WARNING,
                "Your pipeline contains multiple .create(...) or .load(...) steps.",
                "This is fine if it is intentional, but note that calling such a step will reset the pipeline's data."
            )


    def __repr__(self) -> str:
        step_lines = "\n  ".join(repr(s) for s in self._steps)
        return f"PipelineBuilder(\n  {step_lines}\n)"


class PipelineError(Exception):
    """Custom exception for pipeline validation errors."""
