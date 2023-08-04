from decimal import Decimal
from typing import assert_never

from attrs import define, field

from app.domain.base import Entity, field_relationship
from app.domain.iteration import DomainIteration
from app.domain.session import DomainSession
from app.system.constants import DecisionAction
from app.system.exceptions import WrongDecisionError


@define(kw_only=True, slots=False, hash=True)
class DomainDecision(Entity):
    """User decision for particular iteration"""

    session: DomainSession = field_relationship(init=True, repr=True)
    iteration: DomainIteration
    action: DecisionAction
    time_spent: Decimal = field()
    iteration_num: int = field()
    result_raw: Decimal = field()
    result_final: Decimal = field()

    @property
    def price_change(self) -> Decimal:
        price_diff = self.iteration.bar_price_fix - self.iteration.bar_price_finish
        change = round(price_diff / self.iteration.bar_price_finish, 6)
        return Decimal(str(change))

    @iteration_num.default
    def iteration_num_default(self) -> int:
        return self.iteration.iteration_num

    @result_raw.default
    def result_raw_default(self) -> Decimal:
        match self.action:
            case DecisionAction.buy:
                return self.price_change
            case DecisionAction.skip:
                return Decimal(0)
            case DecisionAction.sell:
                return self.price_change * -1
            case _:
                assert_never(self.action)

    @result_final.default
    def result_final_default(self) -> Decimal:
        match self.action:
            case DecisionAction.buy | DecisionAction.sell:
                return self.result_raw - self.session.slippage.value
            case DecisionAction.skip:
                return Decimal(0)
            case _:
                assert_never(self.action)

    @time_spent.validator
    def time_spent_validator(self, attribute: str, value: Decimal) -> None:
        if value < 0:
            raise WrongDecisionError

    @result_final.validator
    def result_final_validator(self, attribute: str, value: Decimal) -> None:
        if value > self.result_raw:
            raise WrongDecisionError
