from app.api.schemas.base import RespData


class RespDataHealthcheck(RespData):
    is_app_up: bool
    is_db_up: bool
