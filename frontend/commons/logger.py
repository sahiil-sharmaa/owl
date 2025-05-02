import json
import logging
from datetime import datetime
from pytz import timezone

class UTCFormatter(logging.Formatter):
    """
    A custom logging formatter to output log records as JSON.

    This formatter converts each log record into a JSON string that includes the log message,
    a UTC timestamp, the log level, and the logger's name. It overrides the default formatting
    behavior to provide more structured and machine-readable log outputs.

    Methods:
        format(self, record): Formats the log record into a JSON string.
    """

    def format(self, record, datefmt=None):
        """
        Format the log record into a JSON string.

        Parameters:
            record (logging.LogRecord): The log record.

        Returns:
            str: A JSON string containing the message, timestamp, log level, and logger's name.
        """
        IST = timezone('Asia/Kolkata')
        dt = datetime.fromtimestamp(record.created, IST)
        dt = dt.strftime("%d-%b-%Y | %I:%M:%S %p")

        log_data = {
            "message": record.getMessage(),
            "timestamp": dt,
        }
        return json.dumps(log_data)


def configure_logger():
    """
    Configures and returns a logger with INFO level and a custom formatter.

    This function sets up a root logger to output logs in JSON format using the UTCFormatter.
    It ensures that all log messages are consistently formatted, making them easier to parse and analyze.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # create formatter
    # formatter = UTCFormatter()
    formatter = logging.Formatter('%(asctime)s | %(lineno)s-%(filename)s | %(message)s \n')

    # Clear existing handlers to prevent duplicate logging
    logger.handlers = []

    # Create and add a console handler with the custom formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(filename='app.log',encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

