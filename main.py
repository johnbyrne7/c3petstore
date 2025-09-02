import logging.config
import uvicorn
from app import create_app

app = create_app()

if __name__ == "__main__":
    logger = logging.getLogger("app")
    logger.info("Starting Uvicorn server on port 8000")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_config=app.middleware.options.config[
            "LOGGING_CONFIG"
        ],  # Use the same logging config
        log_level="info",  # Align with logger level
        access_log=True,
    )
