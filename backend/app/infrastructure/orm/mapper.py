from sqlalchemy import Table
from sqlalchemy.orm import composite, relationship

from app.domain.session import DomainSession
from app.domain.session_decision import DomainDecision
from app.domain.session_provider import Ticker
from app.domain.user import DomainAuth, DomainUser, Email, IpAddress, Password
from app.infrastructure.orm.base import Base, mapper_registry
from app.infrastructure.orm.session import OrmSession
from app.infrastructure.orm.session_decision import OrmDecision
from app.infrastructure.orm.user import OrmAuth, OrmUser


def verify_orm() -> None:
    """Verify if all ORM models are used Declarative defenition approach"""
    all_orm_models = Base.__subclasses__()
    for model in all_orm_models:
        assert_msg = f"The table defenition for {model} not found"
        assert hasattr(model, "__table__") and isinstance(model.__table__, Table), assert_msg


def map_user() -> None:
    mapper_registry.map_imperatively(
        DomainUser,
        OrmUser.__table__,
        properties={
            "email": composite(Email, OrmUser.__table__.c._email),
            "password": composite(Password, OrmUser.__table__.c._password),
            "auths": relationship(DomainAuth, back_populates="user", lazy="dynamic", uselist=True),
            "sessions": relationship(
                DomainSession, back_populates="user", lazy="dynamic", uselist=True
            ),
        },
    )
    mapper_registry.map_imperatively(
        DomainAuth,
        OrmAuth.__table__,
        properties={
            "ip_address": composite(IpAddress, OrmAuth.__table__.c._ip_address),
            "user": relationship(DomainUser, back_populates="auths", lazy="joined", uselist=False),
        },
    )


def map_session() -> None:
    mapper_session = mapper_registry.map_imperatively(
        DomainSession,  # type: ignore[type-abstract]
        OrmSession.__table__,
        polymorphic_on="mode",
        properties={
            "ticker": composite(Ticker.from_json, OrmSession.__table__.c._ticker),
            "user": relationship(
                DomainUser, back_populates="sessions", lazy="joined", uselist=False
            ),
            "decisions": relationship(
                DomainDecision, back_populates="session", lazy="joined", uselist=True
            ),
        },
    )
    for subclass in DomainSession.__subclasses__():
        mapper_registry.map_imperatively(
            subclass,  # type: ignore[type-abstract]
            OrmSession.__table__,
            inherits=mapper_session,
            polymorphic_identity=subclass.__name__.replace(DomainSession.__name__, "").lower(),
        )


def map_decision() -> None:
    mapper_registry.map_imperatively(
        DomainDecision,
        OrmDecision.__table__,
        properties={
            "session": relationship(
                DomainSession, back_populates="decisions", lazy="joined", uselist=False
            ),
        },
    )


def init_orm_mappers() -> None:
    """Single point to setup all domain <-> ORM model mappings"""
    verify_orm()

    # Map domain models with ORM models
    map_user()
    map_session()
    map_decision()
