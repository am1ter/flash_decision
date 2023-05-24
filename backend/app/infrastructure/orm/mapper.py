from sqlalchemy.orm import relationship

from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.orm.auth import OrmAuth
from app.infrastructure.orm.base import mapper_registry
from app.infrastructure.orm.user import OrmUser


def init_orm_mappers() -> None:
    """Single point to setup all domain <-> ORM model mappings"""
    mapper_registry.map_imperatively(
        DomainUser,
        OrmUser,  # type: ignore[arg-type]
        properties={
            "auths": relationship(DomainAuth, back_populates="user", lazy="dynamic", uselist=True)
        },
    )
    mapper_registry.map_imperatively(
        DomainAuth,
        OrmAuth,  # type: ignore[arg-type]
        properties={
            "user": relationship(DomainUser, back_populates="auths", lazy="joined", uselist=False)
        },
    )
