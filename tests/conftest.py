import asyncpg
import pytest

from fair.repository import TestRepository
from settings import settings


@pytest.fixture(autouse=True)
async def clear_repository():
    conn = await asyncpg.connect(settings.DSN)
    await conn.execute("DELETE FROM cars")
    await TestRepository().clear()
