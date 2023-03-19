import json
import logging


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
    logging.basicConfig(level=logging.DEBUG,
                        format=formate, stream=None)
    logger = logging.getLogger()
    filter_ = JsonFilter()
    logger.addFilter(filter_)

    # 将日志输出到文件中
    handler = logging.FileHandler('test.log')
    handler.setFormatter(logging.Formatter(formate))
    logger.addHandler(handler)

    # 移除控制台的处理器
    # for hdlr in logging.root.handlers[:]:
    #     if isinstance(hdlr, logging.StreamHandler):
    #         logging.root.removeHandler(hdlr)

    logger.debug('A debug message')

    filter_.ip = '127.0.0.1'
    filter_.source = 'china'
    logger.info('A message for test')
