from app.schemas.base import RespData


class RespDataHealthcheck(RespData):
    isAppUp: bool
