from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.domain.interfaces.repository import RepositoryUser
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.repositories.scoreboard import RepositoryNoSqlScoreboard
from app.infrastructure.repositories.session import RepositorySessionSql
from app.infrastructure.repositories.session_iteration import RepositoryNoSqlIteration
from app.infrastructure.repositories.user import RepositoryUserSql
from app.infrastructure.units_of_work.base_nosql import UnitOfWorkNoSqlMongo
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.services.scoreboard import ServiceScoreboardGlobal
from app.services.session import ServiceSession
from app.services.session_decision import ServiceDecision
from app.services.session_iteration import ServiceIteration
from app.services.support import ServiceSupport
from app.services.user import ServiceUser
from app.services.user_authorization import ServiceAuthorization
from app.system.config import Settings

# Use FastAPI default tools (dependencies) for OAuth2 authorization protocol implementation
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/{Settings().general.BACKEND_API_PREFIX}/user/sign-in"
)
TokenDep = Annotated[str, Depends(oauth2_scheme)]
SignUpFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# Internal UOWs dependencies
uow_user = UnitOfWorkSqlAlchemy(RepositoryUserSql)
UowUserDep = Annotated[UnitOfWork[RepositoryUser], Depends(uow_user)]
uow_session = UnitOfWorkSqlAlchemy(RepositorySessionSql)
uow_iteration = UnitOfWorkNoSqlMongo(RepositoryNoSqlIteration)
uow_scoreboard = UnitOfWorkNoSqlMongo(RepositoryNoSqlScoreboard)


async def verify_authorization(
    uow: UowUserDep,
    token_encoded: TokenDep,
) -> AsyncGenerator[ServiceAuthorization, Any]:
    """Automatically enter into `ServiceAuthorization` context manager and inject UOW and token"""
    async with ServiceAuthorization(uow, token_encoded) as service_auth:
        yield service_auth


# Internal Services dependencies
ServiceSupportDep = Annotated[ServiceSupport, Depends()]
ServiceUserDep = Annotated[ServiceUser, Depends(ServiceUser(uow_user))]
ServiceSessionDep = Annotated[ServiceSession, Depends(ServiceSession(uow_session))]
ServiceIterationDep = Annotated[ServiceIteration, Depends(ServiceIteration(uow_iteration))]
ServiceDecisionDep = Annotated[ServiceDecision, Depends(ServiceDecision(uow_session))]
ServiceScoreboardGlobalDep = Annotated[
    ServiceScoreboardGlobal, Depends(ServiceScoreboardGlobal(uow_scoreboard))
]
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends(verify_authorization)]
