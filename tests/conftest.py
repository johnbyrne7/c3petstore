import httpx
import pytest
from connexion import request
from sqlalchemy.exc import OperationalError
from unittest.mock import patch, MagicMock


from app import create_app
from contextlib import asynccontextmanager

from models.entities import Pet, Order, OrderPet

TEST_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "pytest_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "logs/pytest.log",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # Root logger
            "level": "DEBUG",
            "handlers": ["pytest_file_handler", "console"],
            "propagate": True,
        },
        "connexion": {
            "level": "INFO",
            "handlers": ["pytest_file_handler"],
            "propagate": False,
        },
        "app": {
            "level": "INFO",
            "handlers": ["pytest_file_handler", "console"],
            "propagate": True,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["pytest_file_handler"],
            "propagate": False,
        },
        "aiosqlite": {  # Suppress noisy aiosqlite logs
            "level": "WARNING",
            "handlers": ["pytest_file_handler"],
            "propagate": False,
        },
        "httpx": {  # Suppress httpx logs to reduce caplog noise
            "level": "WARNING",
            "handlers": ["pytest_file_handler"],
            "propagate": False,
        },
    },
}


TEST_CONFIG = {
    "TESTING": True,
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "LOGGING_CONFIG": TEST_LOGGING_CONFIG,
}

test_sessions = {}


# Module-level mock function using a test_sessions store
@asynccontextmanager
async def mock_get_db_session():
    #  since there is noly one of app.get_session, we cannot use closures in db_session
    #  to assign and get unique db sessions for each test in this mock.
    #  Therefore we will use the test_session dictionary for this purpose
    #  The client header contains the unique session_id for each test
    session_id = request.headers.get("session_id")
    if session_id not in test_sessions:
        raise RuntimeError(f"No session found for session_id: {session_id}")
    session = test_sessions[session_id]
    yield session


@pytest.fixture(scope="module", autouse=True)
async def app():
    app = create_app(TEST_CONFIG)
    async with app.middleware.options.SessionLocal() as session:
        #  create db only once per module
        await init_db(session.bind)
        await session.close()
    yield app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session(app, monkeypatch):
    async with app.middleware.options.SessionLocal() as session:
        # Store the current session in the test session dictionary
        session_id = str(id(session))
        test_sessions[session_id] = session

        # Mock session.commit to call flush instead
        async def mock_commit():
            await session.flush()  # Flush to generate IDs without committing

        monkeypatch.setattr(session, "commit", mock_commit)

        # Mock app.get_session
        monkeypatch.setattr("app.get_session", mock_get_db_session)

        try:
            # Begin a transaction with savepoint for more complex dbs like PostgreSQL if used for tests
            async with session.begin() as transaction:
                try:
                    # Create a savepoint for nested transaction support
                    savepoint = await session.begin_nested()
                    yield session
                except Exception as e:
                    # Roll back to savepoint on error
                    await savepoint.rollback()
                    raise
                else:
                    # Roll back savepoint to ensure no changes persist between tests
                    await savepoint.rollback()
        except OperationalError as e:
            # Handle DB-specific errors (e.g., connection issues)
            raise
        finally:
            # Ensure transaction is rolled back between tests
            if session.in_transaction():
                await session.rollback()
            # Close the session and remove from test_sessions
            await session.close()
            del test_sessions[session_id]


@pytest.fixture(scope="function")
async def client(app, db_session):
    # show Using httpx.ASGITransport to test the ASGI app instead of connexion test_client
    #   tests will have to include await for each client request
    # async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app.middleware),
    #                              follow_redirects=True,
    #                              base_url="http://test") as client:
    with app.test_client() as client:  # connexion synchronous TestClient.
        client.headers.update(
            {
                "Authorization": "Bearer TestJWTtoken",
                "Content-type": "application/json",
                "session_id": str(id(db_session)),
            }
        )
        yield client


@pytest.fixture(scope="function")
async def bad_session(app, db_session):
    # invalidate this session
    mock_connection = MagicMock()
    test_sessions[str(id(db_session))] = mock_connection
    yield db_session


@pytest.fixture(scope="module")
async def make_pets(app):
    async with app.middleware.options.SessionLocal() as session:
        initial_data = [
            Pet(name="bark", description="Noisey", status="sold"),
            Pet(name="whiskers", description="Furry", status="available"),
            Pet(name="zebra", description="obvious", status="available"),
        ]
        for item in initial_data:
            item = session.add(item)
            await session.flush()

        yield initial_data
        await session.rollback()
        await session.close()


@pytest.fixture(scope="module")
async def make_orders(app, make_pets):
    async with app.middleware.options.SessionLocal() as session:
        initial_data = [
            Order(status="placed"),
            Order(status="delivered"),
        ]
        i = 0
        for item in initial_data:
            item = session.add(item)
            await session.flush()
            op = OrderPet(
                order_id=initial_data[i].id, pet_id=make_pets[i].id, quantity=i + 1
            )
            op = session.add(op)
            await session.flush()
            i += 1

        yield initial_data
        await session.rollback()
        await session.close()


async def init_db(engine):
    # Create database tables
    from models.entities import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
