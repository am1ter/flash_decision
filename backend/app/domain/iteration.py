from __future__ import annotations

import random
from typing import TYPE_CHECKING, Self

import pandas as pd
from attrs import define, field

from app.domain.base import Entity, field_relationship
from app.system.exceptions import ProviderInvalidDataError, SessionConfigurationError

if TYPE_CHECKING:
    from decimal import Decimal

    from app.domain.session import DomainSession


@define(kw_only=True, slots=False, hash=True)
class DomainIteration(Entity):
    """
    Every session is divided into several parts - iterations.
    For every iteration the user makes a decision - to buy, to sell or do nothing.
    """

    iteration_num: int = field()
    df_quotes: pd.DataFrame = field(repr=False)
    session: DomainSession = field_relationship(init=True)
    bar_price_start: Decimal = field()
    bar_price_finish: Decimal = field()
    bar_price_fix: Decimal = field()

    @iteration_num.validator
    def _validate_iteration_num(self, attribute: str, value: int) -> None:
        if value > self.session.iterations.value:
            raise SessionConfigurationError

    @bar_price_start.default
    def default_bar_price_start(self) -> Decimal:
        bar_num_start = 0
        bar_price_start = self.df_quotes.iloc[bar_num_start]["open"]
        if bar_price_start < 0:
            raise ProviderInvalidDataError
        return bar_price_start

    @bar_price_finish.default
    def default_bar_price_finish(self) -> Decimal:
        bar_num_finish = self.session.barsnumber.value - 1
        bar_price_finish = self.df_quotes.iloc[bar_num_finish]["close"]
        if bar_price_finish < 0:
            raise ProviderInvalidDataError
        return bar_price_finish

    @bar_price_fix.default
    def default_bar_price_fix(self) -> Decimal:
        bar_num_fix = self.session.barsnumber.value + self.session.fixingbar.value - 1
        bar_price_fix = self.df_quotes.iloc[bar_num_fix]["close"]
        if bar_price_fix < 0:
            raise ProviderInvalidDataError
        return bar_price_fix

    @staticmethod
    def _get_slices(total_df_quotes_bars: int, required_slices: int, slice_len: int) -> list[slice]:
        """
        This algorithm creates random slices with specified parameters.
        1. This algorithm ensures that all slices are within the bounds of the original list and
        that no element of the list is included in more than one slice.
        2. It also ensures that the slices are chosen randomly, and that the function can always
        create the maximum possible number of slices when possible.
        3. The function first checks if it's possible to get the required number of slices of the
        specified length from the list. This is always true, because there is a handler for a such
        type of errors in `SessionTimeSeries` class.
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

    @classmethod
    def create_all(cls, session: DomainSession) -> list[Self]:
        """Create all iterations for a session"""
        slices = cls._get_slices(
            total_df_quotes_bars=session.time_series.total_df_quotes_bars,
            required_slices=session.iterations.value,
            slice_len=session.barsnumber.value + session.fixingbar.value,
        )
        session_iterations = []
        for iter_num in range(session.iterations.value):
            iter_slice = slices[iter_num]
            df_quotes_iter = session.time_series.df_quotes[iter_slice]
            iteration = cls(iteration_num=iter_num, df_quotes=df_quotes_iter, session=session)
            session_iterations.append(iteration)
        return session_iterations
