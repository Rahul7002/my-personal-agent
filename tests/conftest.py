import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.api.deps import get_db
from app.core.limiter import limiter

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_backend_db"

# NullPool ensures connections are created and closed inside the active test's event loop
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def db_session():
    """Provides a fresh transactional database session that rolls back cleanly."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            try:
                yield session
            finally:
                if transaction.is_active:
                    await transaction.rollback()

@pytest.fixture
async def client(db_session: AsyncSession):
    """Provides an HTTP test client with get_db dependency overridden."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# @pytest.fixture(autouse=True)
# def disable_rate_limiter():
#     """Globally disables SlowAPI rate limiting for all tests."""
#     limiter.enabled = False
#     yield
#     limiter.enabled = True