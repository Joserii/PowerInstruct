import logging

class RequestFilter(logging.Filter):
    """Custom log filters"""
    def filter(self, record):
        # Filter out request logs for static files and specific paths
        static_paths = ('/static/', '/favicon.ico', '/templates')
        return not any(path in record.getMessage() for path in static_paths)
