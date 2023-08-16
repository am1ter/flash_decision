from abc import ABCMeta

from pymongo import MongoClient
from pymongo.database import Database

from app.infrastructure.databases.base import Db
from app.system.config import Settings


class DbNoSql(Db, metaclass=ABCMeta):
    """ABC class for describing all NoSQL databases"""


class DbNoSqlMongo(DbNoSql):
    def __init__(self) -> None:
        self.engine: Database = self.get_engine()

    def get_engine(self) -> Database:
        """Connect to the mongo server's database"""
        client: MongoClient = MongoClient(Settings().nosql.NOSQL_URL)
        return client[Settings().nosql.NOSQL_DB_NAME]

    async def healthcheck(self) -> bool:
        return self.engine.client.admin.command("ping") == {"ok": 1.0}
