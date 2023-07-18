import pytest

from app.services.support import ServiceSupport

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def service_support() -> ServiceSupport:
    return ServiceSupport()


class TestServiceSupport:
    async def test_check_sql_connection(self, service_support: ServiceSupport) -> None:
        result = await service_support._check_sql_connection()
        assert result
