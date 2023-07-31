import pytest

from app.domain.support import Healthcheck
from app.services.support import ServiceSupport

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def service_support() -> ServiceSupport:
    return ServiceSupport()


class TestServiceSupport:
    async def test_healthcheck(self, service_support: ServiceSupport) -> None:
        result = await service_support.healthcheck()
        assert isinstance(result, Healthcheck)
