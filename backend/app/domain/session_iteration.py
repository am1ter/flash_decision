from __future__ import annotations

import json
import random
import reprlib
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING, Self

import pandas as pd
from attrs import define, field
from plotly import graph_objs
from plotly.utils import PlotlyJSONEncoder

from app.domain.interfaces.domain import Entity
from app.system.exceptions import (
    IterationNotFoundError,
    ProviderInvalidDataError,
    SessionConfigurationError,
)

if TYPE_CHECKING:
    from decimal import Decimal
    from uuid import UUID

    from app.domain.session import Session, SessionQuotes


@define(kw_only=True, slots=False, hash=True)
class IterationCollection:
    """Container for the Session's Iterations"""

    session_quotes: SessionQuotes | None
    iterations: list[Iteration] = field(factory=list, repr=lambda i: f"{reprlib.repr(i)}")

    @property
    def session(self) -> Session | None:
        return self.session_quotes.session if self.session_quotes else None

    def __getitem__(self, key: int) -> Iteration:
        return self.iterations[key]

    def __len__(self) -> int:
        return len(self.iterations)

    def append(self, iteration: Iteration) -> None:
        self.iterations.append(iteration)

    @staticmethod
    def _calculate_random_slices(
        total_df_quotes_bars: int, required_slices: int, slice_len: int
    ) -> list[slice]:
        """
        This algorithm creates random slices with specified parameters.
        1. This algorithm ensures that all slices are within the bounds of the original list and
        that no element of the list is included in more than one slice.
        2. It also ensures that the slices are chosen randomly, and that the function can always
        create the maximum possible number of slices when possible.
        3. The function first checks if it's possible to get the required number of slices of the
        specified length from the list. This is always true, because there is a handler for a such
        type of errors in `SessionTimeSeries` class.
        NB: The state of the `IterationCollection` are always valid - all corner cases are covered.
        """
        assert required_slices * slice_len <= total_df_quotes_bars, SessionConfigurationError.msg
        slices: list[slice] = []
        while len(slices) < required_slices:
            # All possible start variants
            starts_vars = list(range(total_df_quotes_bars - slice_len + 1))
            for _ in range(required_slices):
                # Restart the entire cycle if all required criteria cannot be met
                if not starts_vars:
                    slices = []
                    break
                start = random.choice(starts_vars)
                slices.append(slice(start, start + slice_len))
                # Remove start points that would cause an overlap with the new slice
                starts_vars = [
                    ps for ps in starts_vars if ps >= start + slice_len or ps + slice_len <= start
                ]
        return slices

    def _run_calculate_random_slices(self) -> list[slice]:
        """Use ProcessPoolExecutor to avoid the EventLoop blocking"""
        assert self.session_quotes and self.session
        total_df_quotes_bars = self.session_quotes.total_df_quotes_bars
        required_slices = self.session.iterations.value
        slice_len = self.session.barsnumber.value + self.session.fixingbar.value
        with ProcessPoolExecutor() as executor:
            future = executor.submit(
                self._calculate_random_slices, total_df_quotes_bars, required_slices, slice_len
            )
            return future.result()

    def create_iterations(self) -> Self:
        """Extract random slices from the full df and create all iterations for the session"""
        assert self.session_quotes and self.session
        slices = self._run_calculate_random_slices()
        self.iterations = []
        for iter_num in range(self.session.iterations.value):
            iter_slice = slices[iter_num]
            iteration = Iteration(
                session_id=self.session._id,
                iteration_num=iter_num,
                df_quotes=self.session_quotes.df_quotes[iter_slice],
                session=self.session,
            )
            self.append(iteration)
        assert len(self.iterations) == self.session.iterations.value
        return self


@define(kw_only=True, slots=False, hash=True)
class Iteration(Entity):
    """
    Every session is divided into several parts - Iterations.
    For every iteration the user makes a decision - to buy, to sell or do nothing.
    It is the part of the `Session` Aggregate.
    """

    session_id: UUID
    iteration_num: int = field()
    df_quotes: pd.DataFrame = field(repr=False)
    session: Session | None = field(repr=False, metadata={"asdict_ignore": True})
    bar_price_start: Decimal = field()
    bar_price_finish: Decimal = field()
    bar_price_fix: Decimal = field()
    chart: str = field(repr=False)

    @iteration_num.validator
    def _validate_iteration_num(self, attribute: str, value: int) -> None:
        if not self.session:
            return
        if value > self.session.iterations.value:
            raise IterationNotFoundError

    @bar_price_start.default
    def default_bar_price_start(self) -> Decimal:
        bar_num_start = 0
        bar_price_start = self.df_quotes.iloc[bar_num_start]["open"]
        if bar_price_start < 0:
            raise ProviderInvalidDataError
        return bar_price_start

    @bar_price_finish.default
    def default_bar_price_finish(self) -> Decimal:
        assert self.session
        bar_num_finish = self.session.barsnumber.value - 1
        bar_price_finish = self.df_quotes.iloc[bar_num_finish]["close"]
        if bar_price_finish < 0:
            raise ProviderInvalidDataError
        return bar_price_finish

    @bar_price_fix.default
    def default_bar_price_fix(self) -> Decimal:
        assert self.session
        bar_num_fix = self.session.barsnumber.value + self.session.fixingbar.value - 1
        bar_price_fix = self.df_quotes.iloc[bar_num_fix]["close"]
        if bar_price_fix < 0:
            raise ProviderInvalidDataError
        return bar_price_fix

    @chart.default
    def default_chart(self) -> str:
        candles = graph_objs.Candlestick(
            x=self.df_quotes.index,
            open=self.df_quotes["open"],
            close=self.df_quotes["close"],
            low=self.df_quotes["low"],
            high=self.df_quotes["high"],
            increasing_line_color="#3c996e",
            decreasing_line_color="#e15361",
        )
        chart_data = graph_objs.Figure(data=[candles])
        chart_json = json.dumps(chart_data, cls=PlotlyJSONEncoder)
        return chart_json
