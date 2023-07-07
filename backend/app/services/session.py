from typing import Annotated, assert_never

from fastapi import Depends

from app.api.schemas.session import ReqSession
from app.bootstrap import Bootstrap
from app.domain.session import (
    DomainSession,
    DomainSessionBlitz,
    DomainSessionClassic,
    DomainSessionCrypto,
    DomainSessionCustom,
    SessionOptions,
)
from app.domain.session_provider import Provider
from app.domain.user import DomainUser
from app.infrastructure.repositories.session import RepositorySessionSQL
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSQLAlchemy
from app.system.constants import SessionMode, TickerType
from app.system.logger import create_logger

logger = create_logger("backend.service.session")

# Internal dependencies
uow_session = UnitOfWorkSQLAlchemy(RepositorySessionSQL)
UowSessionDep = Annotated[UnitOfWorkSQLAlchemy, Depends(uow_session)]


class ServiceSession:
    """
    Session is the key object of the application. This service determine how user interacts with it.
    """

    def __init__(self, uow: UowSessionDep) -> None:
        self.uow = uow
        self.provider_stocks = Bootstrap().provider_stocks
        self.provider_crypto = Bootstrap().provider_crypto

    async def collect_session_options(self) -> SessionOptions:
        all_ticker_stocks = list(self.provider_stocks.get_tickers().values())
        all_ticker_crypto = list(self.provider_crypto.get_tickers().values())
        options = SessionOptions(all_ticker=all_ticker_stocks + all_ticker_crypto)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True)
        return options

    def _find_provider(self, ticker_type: str) -> Provider:
        match TickerType(ticker_type):
            case TickerType.crypto:
                provider = self.provider_crypto
            case _:
                provider = self.provider_stocks
        return provider

    def _create_session(
        self, mode: SessionMode, session_params: ReqSession | None
    ) -> DomainSession:
        session: DomainSession
        match mode:
            case SessionMode.classic:
                session = DomainSessionClassic.create(provider=self.provider_stocks)
            case SessionMode.blitz:
                session = DomainSessionBlitz.create(provider=self.provider_stocks)
            case SessionMode.crypto:
                session = DomainSessionCrypto.create(provider=self.provider_crypto)
            case SessionMode.custom:
                assert session_params
                session = DomainSessionCustom.create(
                    provider=self._find_provider(session_params.ticker_type),
                    ticker_symbol=session_params.ticker_symbol,
                    timeframe=session_params.timeframe,
                    barsnumber=session_params.barsnumber,
                    timelimit=session_params.timelimit,
                    iterations=session_params.iterations,
                    slippage=session_params.slippage,
                    fixingbar=session_params.fixingbar,
                )
            case _:
                assert_never(mode)
        return session

    async def start_session(
        self, mode: SessionMode, session_params: ReqSession | None, user: DomainUser
    ) -> DomainSession:
        # Create session
        session = self._create_session(mode, session_params)
        # Link to user
        session.bound_to_user(user)
        # Save session to the database
        async with self.uow:
            self.uow.repository.add(session)
            await self.uow.commit()
        # Start session
        await session.start()
        return session
