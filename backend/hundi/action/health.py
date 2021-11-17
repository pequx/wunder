import logging
import psutil
import json

from hundi.config.settings import DEVELOPMENT
from hundi.config.message import HEALTH_CHECK, HEALTH_CHECK_RESULT
from lib import helper

logger = logging.getLogger(__name__)


def check(source: str):
    logger.info(HEALTH_CHECK.format(source))
    stats = {
        "timestamp": helper.get_timestamp(),
        "boot_time": psutil.boot_time(),
        "load_avg": psutil.getloadavg(),
        "cpu_times": psutil.cpu_times(),
        "cpu_stats": psutil.cpu_stats(),
        "cpu_count": psutil.cpu_count(),
        "virtual_memory": psutil.virtual_memory(),
        "swap_memory": psutil.swap_memory(),
        "disk_partitions": psutil.disk_partitions(),
        "disk_usage": psutil.disk_usage('/'),
        "disk_io_counters": psutil.disk_io_counters(perdisk=False),
        "sensors_battery": psutil.sensors_battery(),
        "pids": psutil.pids()
    }
    result = json.dumps(stats)
    logger.info(HEALTH_CHECK_RESULT.format(stats))
    return result
