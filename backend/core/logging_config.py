"""
Production-ready logging configuration for LOKI
Supports JSON structured logging, log aggregation, and multiple handlers
"""
import logging
import logging.config
import os
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Add custom fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['environment'] = os.getenv('FLASK_ENV', 'production')
        log_record['service'] = 'loki-backend'

        # Add trace information if available
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id
        if hasattr(record, 'span_id'):
            log_record['span_id'] = record.span_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id


def setup_logging(app=None):
    """
    Setup logging configuration for production

    Features:
    - JSON structured logging for log aggregation
    - Multiple handlers (console, file, error file)
    - Configurable log levels
    - Request ID tracking
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', 'json')  # json or text

    # Create logs directory if it doesn't exist
    log_dir = os.getenv('LOG_DIR', '/app/logs')
    os.makedirs(log_dir, exist_ok=True)

    # Define formatters
    if log_format == 'json':
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Application log file handler
    app_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/loki-app.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)

    # Error log file handler
    error_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/loki-error.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Access log file handler (for request logging)
    access_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/loki-access.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    # Configure Flask app logger if provided
    if app:
        app.logger.handlers = []
        app.logger.addHandler(console_handler)
        app.logger.addHandler(app_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(log_level)

    # Configure access logger
    access_logger = logging.getLogger('loki.access')
    access_logger.handlers = []
    access_logger.addHandler(access_handler)
    access_logger.addHandler(console_handler)
    access_logger.setLevel(logging.INFO)

    # Suppress noisy third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logging.info("Logging configured successfully", extra={
        'log_level': log_level,
        'log_format': log_format,
        'log_dir': log_dir
    })


def get_request_logger():
    """Get logger for request logging"""
    return logging.getLogger('loki.access')


def log_request(request, response, duration_ms):
    """
    Log HTTP request with structured data

    Args:
        request: Flask request object
        response: Flask response object
        duration_ms: Request duration in milliseconds
    """
    logger = get_request_logger()

    log_data = {
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code,
        'duration_ms': duration_ms,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'content_length': response.content_length,
    }

    # Add request ID if available
    if hasattr(request, 'request_id'):
        log_data['request_id'] = request.request_id

    # Add user ID if available (from auth)
    if hasattr(request, 'user_id'):
        log_data['user_id'] = request.user_id

    logger.info('HTTP request', extra=log_data)


class RequestLogger:
    """
    Flask middleware for request logging
    """
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        import uuid
        from flask import g

        @app.before_request
        def before_request():
            """Set up request logging"""
            from time import time
            g.start_time = time()
            g.request_id = str(uuid.uuid4())

        @app.after_request
        def after_request(response):
            """Log request after completion"""
            from time import time
            if hasattr(g, 'start_time'):
                duration_ms = (time() - g.start_time) * 1000
                log_request(request, response, duration_ms)
            return response
