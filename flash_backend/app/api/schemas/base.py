from pydantic import BaseModel, Extra


class RespMeta(BaseModel):
    class Config:
        extra = Extra.allow


class RespData(BaseModel):
    class Config:
        extra = Extra.allow


class Resp(BaseModel):
    meta: RespMeta | None
    data: RespData
