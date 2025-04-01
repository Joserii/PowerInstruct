import logging

class RequestFilter(logging.Filter):
    """自定义日志过滤器"""
    def filter(self, record):
        # 过滤掉静态文件和特定路径的请求日志
        static_paths = ('/static/', '/favicon.ico', '/templates')
        return not any(path in record.getMessage() for path in static_paths)
