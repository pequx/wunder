from decouple import config


ENVIRONMENT = config("HUNDI_ENVIRONMENT", default="local")
BUILD = True if ENVIRONMENT == "build" else False
DEVELOPMENT = True if ENVIRONMENT == "development" else False
PRODUCTION = True if ENVIRONMENT == "production" else False
DEBUG = config("HUNDI_DEBUG", default=False, cast=bool)

KAIROSDB_URL = config("KAIROSDB_URL", default="http://localhost:8080")
KAIROSDB_API_DATAPOINTS = config("KAIROSDB_API_DATAPOINTS", default="/api/v1/datapoints")
KAIROSDB_TTL = config("KAIROSDB_TTL", default=15 * 365 * 24 * 60 * 60, cast=int)

LOG_PATH = config("HUNDI_LOG_PATH", default="./hundi.log")
LOG_QUEUE_MAX_SIZE = config("HUNDI_LOG_QUEUE_MAX_SIZE", default=100, cast=int)
LOG_UPDATE_INTERVAL = config("HUNDI_LOG_UPDATE_INTERVAL", default=0.5, cast=float)
LOG_MAX_LINES = config("HUNDI_LOG_MAX_LINES", default=1000, cast=int)
LOG_LEVEL = config("HUNDI_LOG_LEVEL", default=1000, cast=int)
