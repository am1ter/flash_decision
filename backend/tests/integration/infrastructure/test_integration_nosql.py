import pytest
from pymongo.errors import ConnectionFailure

from app.infrastructure.nosql import DbNoSql, DbNoSqlMongo


@pytest.fixture()
def db_nosql() -> DbNoSql:
    return DbNoSqlMongo()


class TestNoSql:
    def test_connection(self, db_nosql: DbNoSql) -> None:
        """Make sure the database is up and a connection to it can be established"""
        try:
            db_nosql.engine.client.admin.command("ping")
        except ConnectionFailure:
            pytest.fail("Connection to the NoSQL server cannot be established")
