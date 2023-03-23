import logging
import json
from logging.handlers import RotatingFileHandler
from common import ATTACHMENT
from common import CONSOLE_OUTPUT


class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            'time': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage()
        }
        if hasattr(record, 'username'):
            data['username'] = record.username
        if hasattr(record, 'password'):
            data['password'] = record.password
        # module 指的是模块名
        # data['module'] = record.module
        data['line'] = record.lineno
        # ensure_ascii 设置为 True（默认值） 所有非 ASCII 字符都会被转义为 Unicode 转义序列
        # (如\uXXXX）并以 ASCII 编码输出。如果 ensure_ascii 设置为 False，则所有非 ASCII 字符都将原样输出到 JSON 字符串中
        return json.dumps(data, ensure_ascii=False)


class UserLogFilter(logging.Filter):
    def filter(self, record):
        ext_field = ''
        if hasattr(record, 'username'):
            ext_field += '账号 {}'.format(record.username)
        if hasattr(record, 'password'):
            ext_field += ' 密码 {}'.format(record.password)
        record.ext_field = ext_field
        return True


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
            backupCount=backup_count,
            encoding='utf-8'
        )
        # 模式2
        debug_info = logging.Filter()
        debug_info.filter = lambda record: record.levelno == logging.INFO
        handler_info = RotatingFileHandler(
            filename=f'{self.base_dir}/{platform_path}/info.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        # 模式3
        debug_warning = logging.Filter()
        debug_warning.filter = lambda record: record.levelno == logging.WARNING
        handler_warning = RotatingFileHandler(
            filename=f'{self.base_dir}/{platform_path}/warning.log',
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # 添加 StreamHandler 将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s %(ext_field)s')
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(UserLogFilter())
        # 配置用于控制台输出
        if CONSOLE_OUTPUT:
            self.logger.addHandler(console_handler)

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
