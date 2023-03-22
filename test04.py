import logging
import json
from logging.handlers import RotatingFileHandler


class MyLogger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 创建 RotatingFileHandler 对象，并设置日志文件名、备份份数
        max_bytes = 10 * 1024 * 1024  # 10 MB
        backup_count = 100

        # 模式1
        debug_filter = logging.Filter()
        debug_filter.filter = lambda record: record.levelno == logging.DEBUG
        handler_debug = RotatingFileHandler(
            filename='attachment/debug.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        # 模式2
        debug_info = logging.Filter()
        debug_info.filter = lambda record: record.levelno == logging.INFO
        handler_info = RotatingFileHandler(
            filename='attachment/info.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        # 模式3
        debug_warning = logging.Filter()
        debug_warning.filter = lambda record: record.levelno == logging.WARNING
        handler_warning = RotatingFileHandler(
            filename='attachment/warning.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count
        )

        # 设置过滤
        handler_debug.addFilter(debug_filter)
        handler_info.addFilter(debug_info)
        handler_warning.addFilter(debug_warning)
        # 设置每个 handler 的日志级别
        handler_debug.setLevel(logging.DEBUG)
        handler_info.setLevel(logging.INFO)
        handler_warning.setLevel(logging.WARNING)
        # 配置日志输出格式
        formatter = JSONFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(custom_field)s')
        handler_debug.setFormatter(formatter)
        handler_info.setFormatter(formatter)
        handler_warning.setFormatter(formatter)

        # 将 handler 添加到 logger 中
        self.logger.addHandler(handler_debug)
        self.logger.addHandler(handler_info)
        self.logger.addHandler(handler_warning)

    def debug(self, message, extra=None):
        if extra is None:
            extra = {}
        extra['custom_field'] = 'custom_value'
        self.logger.debug(message, extra=extra)

    def info(self, message, extra=None):
        if extra is None:
            extra = {}
        extra['custom_field'] = 'custom_value'
        self.logger.info(message, extra=extra)

    def warning(self, message, extra=None):
        if extra is None:
            extra = {}
        extra['custom_field'] = 'custom_value'
        self.logger.warning(message, extra=extra)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            'time': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'line': record.lineno,
            'custom_field': record.custom_field,
        }
        return json.dumps(data)


if __name__ == '__main__':
    my_logger = MyLogger()
    my_logger.debug('This is a debug-level message', {'my_custom_field': 'my_custom_value'})
    my_logger.info('This is a debug-level message', {'my_custom_field': 'my_custom_value'})
    my_logger.warning('This is a debug-level message', {'my_custom_field': 'my_custom_value'})
