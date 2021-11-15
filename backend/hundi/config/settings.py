import os

from decouple import config


ENVIRONMENT = os.environ.get("HUNDI_ENVIRON", config(
    "HUNDI_ENVIRON", default="development")
)

DEVELOPMENT = True if ENVIRONMENT == "development" else False
PRODUCTION = True if ENVIRONMENT == "production" else False
DEBUG = os.environ.get("HUNDI_DEBUG", config("HUNDI_DEBUG", default=False))

KAIROSDB_URL = os.environ.get("KAIROSDB_URL", config(
    "KAIROSDB_URL", default="http://localhost:8080")
)
KAIROSDB_API_DATAPOINTS = os.environ.get("KAIROSDB_API_DATAPOINTS", config(
    "KAIROSDB_API_DATAPOINTS", default="/api/v1/datapoints"))
KAIROSDB_TTL = int(
    os.environ.get("KAIROSDB_TTL", config(
        "KAIROSDB_TTL", default=15 * 365 * 24 * 60 * 60)
    )
)

