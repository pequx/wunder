import logging
import urllib
import json
import requests
import time
import sys
import traceback
import pandas

from hundi.config.message import (
    QUERY_CURRENT,
    QUERY_EXCEPTION,
    KAIROSDB_ERROR_RESPONSE_STATUS,
    KAIROSDB_ERROR_DECODING_JSON,
    KAIROSDB_NO_EXPECTED_TAG
)
from hundi.config.settings import (
    KAIROSDB_URL,
    KAIROSDB_API_DATAPOINTS
)

logger = logging.getLogger(__name__)


def query(
    metric_name: str,
    time_unit: str = "minutes",
    start_relative: int = 5,
    end_relative: int = 0,
    cache_time: int = 300,
    tags={},
    group_by=[],
    aggregators=[],
):
    """Generic low-level KairosDB query formatter

    TODO: support for absolute time
    """
    query = {
        "metrics": [
            {
                "tags": tags,
                "name": metric_name,
            }
        ],
        "cache_time": cache_time,
        "start_relative": {"value": start_relative, "unit": time_unit},
    }

    if end_relative != 0:
        query["end_relative"] = {"value": end_relative, "unit": time_unit}
    if len(group_by) > 0:
        query["metrics"][0]["group_by"] = group_by
    if len(aggregators) > 0:
        query["metrics"][0]["aggregators"] = aggregators

    try:
        logger.debug(QUERY_CURRENT.format(query))
        query = urllib.parse.quote(json.dumps(query))
        r = requests.get(
            KAIROSDB_URL + KAIROSDB_API_DATAPOINTS + "/query?query=" + query
        )
    except Exception as e:
        logger.warning(QUERY_EXCEPTION.format(e.message))
        sys.stderr.write(
            "### {} ".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        )
        traceback.print_exc()
        return False

    if r.status_code != 200:
        try:
            errors = json.loads(r.content)["errors"]
        except ValueError:
            errors = ["no errors returned"]
        except KeyError:
            errors = ["no errors key found"]
        logger.warning(
            KAIROSDB_ERROR_RESPONSE_STATUS.format(
                r.status_code, ", ".join(errors)
            )
        )
        return False

    try:
        response = json.loads(r.content)
    except ValueError:
        logger.warning(KAIROSDB_ERROR_DECODING_JSON.format(r.content))
        return False

    return response


def query_as_dataframe(
    metric_name: str,
    columns: str,
    time_unit: str,
    start_relative: int,
    end_relative: int,
    cache_time: int,
    aggregators,
):
    """
    FIXME: metric_name should correspond to time_unit, otherwise we
    trigger grouping mechanism which is WRONG!
    """
    group_by = [{"name": "tag", "tags": ["column"]}]
    logger.debug(columns)
    tags = {"column": columns}
    r = query(
        metric_name,
        time_unit=time_unit,
        start_relative=start_relative,
        end_relative=end_relative,
        cache_time=cache_time,
        tags=tags,
        group_by=group_by,
        aggregators=aggregators,
    )
    if r is False:
        return None

    results = r["queries"][0]["results"]

    data = {}
    for result in results:
        logger.debug(result)
        if "column" not in result["tags"]:
            logger.warning(KAIROSDB_NO_EXPECTED_TAG.format("column"))
            return None
        column_name = result["tags"]["column"][0]
        values = map(lambda x: x[1], result["values"])
        index = map(
            lambda x: pandas.to_datetime(x[0], unit="ms"), result["values"]
        )
        data[column_name] = pandas.Series(values, index=index)

    return pandas.DataFrame(data)
