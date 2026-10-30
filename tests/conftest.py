import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.api.deps import get_db
from app.core.limiter import limiter

# 1. Import your SQLAlchemy Base where your models (like User) are registered.
# (If your Base is located in app.db.base or app.models, update this import path accordingly)
from app.models.user import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_backend_db"

# NullPool ensures connections are created and closed inside the active test's event loop
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# 2. Add this fixture: It automatically runs before test execution to build tables
@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create all tables in the fresh Postgres container, then drop them on teardown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

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