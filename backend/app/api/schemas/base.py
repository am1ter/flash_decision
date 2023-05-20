from pydantic import BaseModel, Extra


class ReqMeta(BaseModel):
    class Config:
        extra = Extra.allow


class RespMeta(BaseModel):
    class Config:
        extra = Extra.allow


class RespData(BaseModel):
    class Config:
        extra = Extra.allow


class Resp(BaseModel):
    meta: RespMeta | None
    data: RespData
