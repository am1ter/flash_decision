from app.bootstrap import Bootstrap

type(Bootstrap)._instances = {}
Bootstrap(start_orm=True, provider_crypto=None, provider_stocks=None)  # type: ignore[arg-type]
