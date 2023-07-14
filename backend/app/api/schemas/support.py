from app.api.schemas.base import RespData


class RespDataHealthcheck(RespData):
    is_app_up: bool
    is_db_up: bool
    is_cache_up: bool
    is_provider_stocks_up: bool
    is_provider_crypto_up: bool
