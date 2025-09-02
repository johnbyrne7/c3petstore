# Settings common to all environments (development|staging|production)
# Place environment specific settings in env_settings.py

APP_NAME = "ConnexionPetStore"
JWT_ALGORITHM = "HS256"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",  # Less verbose in production
            "formatter": "standard",
            "filename": "logs/info.log",  # you may want to put in /var/logs in production
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": "logs/error.log",  # you may want to put in /var/logs in production
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "logs/debug.log",  # you may want to put in /var/logs in production
            "maxBytes": 10485760,
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": [
                "info_file_handler",
                "error_file_handler",
                "debug_file_handler",
            ],
            "propagate": False,
        },
        "connexion": {
            "level": "INFO",
            "handlers": ["info_file_handler"],
            "propagate": False,
        },
        "app": {
            "level": "INFO",
            "handlers": [
                "info_file_handler",
                "error_file_handler",
                "debug_file_handler",
            ],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["info_file_handler"],
            "propagate": False,
        },
    },
}
