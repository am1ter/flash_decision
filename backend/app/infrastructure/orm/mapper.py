from sqlalchemy import Table
from sqlalchemy.orm import composite, relationship

from app.domain.user import DomainAuth, DomainUser, Email, IpAddress, Password
from app.infrastructure.orm.base import Base, mapper_registry
from app.infrastructure.orm.user import OrmAuth, OrmUser


def init_orm_mappers() -> None:
    """Single point to setup all domain <-> ORM model mappings"""

    # Verify if all ORM models are used Declarative defenition approach
    all_orm_models = Base.__subclasses__()
    for model in all_orm_models:
        assert_msg = f"The table defenition for {model} not found"
        assert hasattr(model, "__table__") and isinstance(model.__table__, Table), assert_msg

    # Map domain models with ORM models
    mapper_registry.map_imperatively(
        DomainUser,
        OrmUser.__table__,
        properties={
            "email": composite(Email, OrmUser.__table__.c._email),
            "password": composite(Password, OrmUser.__table__.c._password),
            "auths": relationship(DomainAuth, back_populates="user", lazy="dynamic", uselist=True),
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
