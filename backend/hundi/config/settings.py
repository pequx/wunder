import os

from decouple import config


ENVIRONMENT = os.environ.get("HUNDI_ENVIRONMENT", config(
    "HUNDI_ENVIRONMENT", default="development")
)
BUILD = True if ENVIRONMENT == "build" else False
DEVELOPMENT = True if ENVIRONMENT == "development" else False
PRODUCTION = True if ENVIRONMENT == "production" else False
DEBUG = os.environ.get("HUNDI_DEBUG", config("HUNDI_DEBUG", default=False, cast=bool))

KAIROSDB_URL = os.environ.get("KAIROSDB_URL", config(
    "KAIROSDB_URL", default="http://localhost:8080")
)
KAIROSDB_API_DATAPOINTS = os.environ.get("KAIROSDB_API_DATAPOINTS", config(
    "KAIROSDB_API_DATAPOINTS", default="/api/v1/datapoints"))
KAIROSDB_TTL: int = int(
    os.environ.get("KAIROSDB_TTL", config(
        "KAIROSDB_TTL", default=15 * 365 * 24 * 60 * 60, cast=int)
    )
)
LOG_PATH = os.environ.get(
    "HUNDI_RELATIVE_LOG_PATH",
    config(
        "HUNDI_RELATIVE_LOG_PATH",
        default="../../logs/hundi.log"))

LOG_QUEUE_MAX_SIZE = os.environ.get(
    "HUNDI_LOG_QUEUE_MAX_SIZE",
    config(
        "HUNDI_LOG_QUEUE_MAX_SIZE",
        default=100, cast=int))
