from attrs import define


@define(kw_only=True, slots=False, hash=True)
class HealthCheck:
    is_app_up: bool = True
    is_sql_up: bool
    is_cache_up: bool
    is_provider_stocks_up: bool
    is_provider_crypto_up: bool
