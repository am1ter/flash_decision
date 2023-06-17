import pytest

from app.bootstrap import Bootstrap
from app.services.support import ServiceSupport
from tests.unit.services.conftest import fake_db_connection

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def service_support() -> ServiceSupport:
    Bootstrap(start_orm=True, db_conn_factory=fake_db_connection)
    return ServiceSupport()


class TestServiceSupport:
    async def test_check_db_connection(self, service_support: ServiceSupport) -> None:
        result = await service_support.check_db_connection()
        assert result
