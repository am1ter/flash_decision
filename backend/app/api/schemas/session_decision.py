from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.api.schemas.base import RespData


class ReqRecordDecision(BaseModel):
    session_id: UUID
    iteration_num: int
    action: str
    time_spent: Decimal


class RespDecision(RespData):
    result_final: Decimal
