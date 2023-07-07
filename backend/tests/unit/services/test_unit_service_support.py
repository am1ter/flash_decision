import pytest

from app.services.support import ServiceSupport

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def service_support() -> ServiceSupport:
    return ServiceSupport()


class TestServiceSupport:
    async def test_check_db_connection(self, service_support: ServiceSupport) -> None:
        result = await service_support.check_db_connection()
        assert result
