from app.api.schemas.base import RespData


class RespIteration(RespData):
    iteration_num: int
    chart: str
