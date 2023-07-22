from abc import ABCMeta, abstractmethod
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from app.system.config import Settings


class DbNoSql(metaclass=ABCMeta):
    """ABC class for describing all NoSQL databases"""

    def __init__(self) -> None:
        self.engine = self.get_engine()

    @abstractmethod
    def get_engine(self) -> Any:
        """All no sql db configuration for concrete classes must be done here"""


class DbNoSqlMongo(DbNoSql):
    def get_engine(self) -> Database:
        """Connect to the mongo server's database"""
        client: MongoClient = MongoClient(Settings().nosql.NOSQL_URL)
        return client[Settings().nosql.NOSQL_DB_NAME]
