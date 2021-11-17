import datetime
import logging
import sys
import os

from hundi.config.settings import LOG_PATH


class LogFormatter(logging.Formatter):
    NAME_LENGTH = 20
    converter = datetime.datetime.fromtimestamp

    def format(self, record):
        orig_name = record.name
        name = orig_name
        if len(name) > self.NAME_LENGTH:
            name_splitted = name.split(".")
            for idx, val in enumerate(name_splitted[:-1]):
                name_splitted[idx] = name_splitted[idx][0]
                if len(".".join(name_splitted)) <= self.NAME_LENGTH:
                    break
            name = ".".join(name_splitted)
            if len(name) > self.NAME_LENGTH:
                name = name[-self.NAME_LENGTH:]

        record.name = name
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s


def initialize_logging(log_level: int):
    #    formatter = logging.Formatter("%(asctime)s %(filename)s: " +
    # fmt.format("%(levelname)s") + " %(message)s",
    #                                  "%Y/%m/%d %H:%M:%S")

    if log_level is logging.DEBUG:
        os.environ.setdefault('HUNDI_DEBUG', "True")

    style = "%(asctime)s %(levelname)8s [%(threadName)10s] [%(name)20s:%(lineno)-4s] %(message)s"
    formatter = LogFormatter(style)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    logging.basicConfig(filename=LOG_PATH, encoding='utf-8', level=logging.DEBUG, format=style)

    logging.root.setLevel(log_level)
    logging.root.addHandler(handler)

    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARN)
