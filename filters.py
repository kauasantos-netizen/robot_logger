import logging

class N8NFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ["WARNING", "ERROR", "END"]