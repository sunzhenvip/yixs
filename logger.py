import logging
import json
from logging.handlers import RotatingFileHandler
from common import ATTACHMENT


class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            'time': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'line': record.lineno,
        }
        if hasattr(record, 'username'):
            data['username'] = record.username
        if hasattr(record, 'password'):
            data['password'] = record.password
        return json.dumps(data)


class MyLogger:
    base_dir = ATTACHMENT

    def __init__(self, platform_path):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 创建 RotatingFileHandler 对象，并设置日志文件名、备份份数
        max_bytes = 10 * 1024 * 1024  # 10 MB
        backup_count = 100

        # 模式1
        debug_filter = logging.Filter()
        debug_filter.filter = lambda record: record.levelno == logging.DEBUG
        handler_debug = RotatingFileHandler(
            filename=f'{self.base_dir}/{platform_path}/debug.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        # 模式2
        debug_info = logging.Filter()
        debug_info.filter = lambda record: record.levelno == logging.INFO
        handler_info = RotatingFileHandler(
            filename=f'{self.base_dir}/{platform_path}/info.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        # 模式3
        debug_warning = logging.Filter()
        debug_warning.filter = lambda record: record.levelno == logging.WARNING
        handler_warning = RotatingFileHandler(
            filename=f'{self.base_dir}/{platform_path}/warning.log',
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
        self.logger.debug(message, extra=extra)

    def info(self, message, extra=None):
        if extra is None:
            extra = {}
        self.logger.info(message, extra=extra)

    def warning(self, message, extra=None):
        if extra is None:
            extra = {}
        self.logger.warning(message, extra=extra)