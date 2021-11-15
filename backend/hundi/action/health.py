import logging
import psutil
import json

from config.settings import DEVELOPMENT
from config.message import HEALTH_CHECK
from lib import helper

logger = logging.getLogger(__name__)


class Health(object):
    def __init__(self, source: str):
        self.source = source
        self.stats = {}

    def check(self):
        logger.info(HEALTH_CHECK.format(self.source))
        self.colonoscopy()
        return True

    def colonoscopy(self):
        self.stats = {
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
        logger.info(json.dumps(self.stats))
