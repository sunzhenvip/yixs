import json
import logging
import datetime
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler


class JsonFilter(logging.Filter):
    ip = 'IP'
    source = 'APP'

    def filter(self, record):
        record.ip = self.ip
        record.source = self.source
        return True


if __name__ == '__main__':
    formate = json.dumps({
        "time": "%(asctime)s",
        "levelname": "%(levelname)s",
        "levelno": "%(lineno)d",
        "ip": "%(ip)s",
        "source": "%(source)s"
    })
    logger = logging.getLogger()
    filter_ = JsonFilter()
    logger.addFilter(filter_)

    # 将日志输出到文件中
    # handler = logging.FileHandler('attachment/test.log')
    # handler.setFormatter(logging.Formatter(formate))
    # 设置日志文件最大10M，备份数量为5个

    # 获取当前日期和时间，并格式化为可读字符串
    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d_%H%M%S")
    max_bytes = 1 * 1024 * 1024  # 1 MB
    backup_count = 5
    handler = RotatingFileHandler(
        filename=f'attachment/test_{date_string}.log',  # 在文件名中添加日期和时间戳信息
        mode='a',  # append to existing file
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setFormatter(logging.Formatter(formate))
    logger.addHandler(handler)

    logging.basicConfig(level=logging.DEBUG,
                        format=formate,
                        handlers=[handler, ],
                        force=True)

    logger.debug('A debug message')

    filter_.ip = '127.0.0.1'
    filter_.source = 'china'
    logger.info('A message for test')

    filter_.ip = '127.0.0.1'
    filter_.source = 'china'
    logger.info('A message for test')

    for i in range(11000):
        filter_.ip = '127.0.0.1'
        filter_.source = 'china'
        logger.info('A message for test')
