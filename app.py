from typing import AsyncIterator, Optional, Dict
from copy import deepcopy
from contextlib import asynccontextmanager

from connexion.options import SwaggerUIOptions
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from connexion import AsyncApp, ConnexionMiddleware, request

import settings


base_config = {
    "specification": "openapi.yaml",
    "DATABASE_URL": "sqlite+aiosqlite:///petstore.db",
    "TESTING": False,
}


async def lifespan_handler(app: ConnexionMiddleware) -> AsyncIterator:
    """Called at startup and shutdown, can yield state which will be available on the
    request."""

    # Store SessionLocal in app state for access in views
    #   Store config in app state as well
    config = deepcopy(app.options.config)
    yield {"SessionLocal": app.options.SessionLocal, "config": config}


@asynccontextmanager
async def get_session():
    async with request.state.SessionLocal() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def create_app(override_settings: Optional[Dict] = None):
    options = SwaggerUIOptions(swagger_ui_path="/docs")
    app = AsyncApp(__name__, specification_dir="./", lifespan=lifespan_handler, swagger_ui_options=options)
    config = deepcopy(base_config)
    config.update(dict_from_module(settings))
    if override_settings:
        config.update(override_settings)
    app.add_api(config["specification"], async_=True, swagger_ui_options=options)
    # Put config in connexion middleware options temporarily
    app.middleware.options.config = config
    engine = create_async_engine(config.get("DATABASE_URL"), echo=False)
    app.middleware.options.SessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    return app


def dict_from_module(module):
    context = {}
    for setting in dir(module):
        if not setting.startswith("_"):
            context[setting] = getattr(module, setting)
    return context


if __name__ == "__main__":
    app = create_app()
    app.run(port=8080)
