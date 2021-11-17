import time
import requests
import logging
import json

from hundi.config.settings import (
    KAIROSDB_TTL, KAIROSDB_URL, KAIROSDB_API_DATAPOINTS
)

from hundi.config.message import (
    KAIROSDB_POSTING,
    KARIOSDB_DATAPOINTS_PUT,
    KAIROSDB_DATAPOINTS_PUT_EXCEPTION,
    KAIROSDB_ERROR_RESPONSE_STATUS
)

logger = logging.getLogger(__name__)


def put_datapoints(metric_name, datapoints, tags=None, ttl=KAIROSDB_TTL):
    t = tags
    if t is None:
        t = {"host": "localhost"}

    data = [
        {
            "name": metric_name,
            "datapoints": datapoints,
            "tags": t,
            "ttl": ttl,
        }
    ]

    try:
        logger.debug(KAIROSDB_POSTING.format(data))
        size = len(datapoints)

        if size < 1:
            return Exception("Invalid data size.")

        start = time.time()
        response = requests.post(KAIROSDB_URL + KAIROSDB_API_DATAPOINTS, json.dumps(data))
        if response.status_code != 204:
            return Exception(KAIROSDB_ERROR_RESPONSE_STATUS.format(response.status_code, response.text))

        end = time.time()
        duration = end - start
        logger.debug(KARIOSDB_DATAPOINTS_PUT.format(size, metric_name, duration, size / duration))

        return True
    except Exception as e:
        logger.exception(KAIROSDB_DATAPOINTS_PUT_EXCEPTION.format(e))

        return False
