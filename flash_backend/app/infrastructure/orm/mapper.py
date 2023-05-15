from sqlalchemy.orm import relationship

from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.orm.auth import OrmAuth
from app.infrastructure.orm.base import mapper_registry
from app.infrastructure.orm.user import OrmUser


def init_orm_mappers() -> None:
    """Domain <-> ORM model mapping"""
    mapper_registry.map_imperatively(
        DomainUser,
        OrmUser,
        properties={
            "auths": relationship(DomainAuth, back_populates="user", lazy="joined", uselist=True)
        },
    )
    mapper_registry.map_imperatively(
        DomainAuth,
        OrmAuth,
        properties={
            "user": relationship(DomainUser, back_populates="auths", lazy="joined", uselist=False)
        },
    )
