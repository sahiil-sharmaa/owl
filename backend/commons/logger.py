import logging

# custom logging function
def configure_logger() -> logging.Logger:
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s | %(lineno)s-%(filename)s | %(message)s \n')

    file_handler = logging.FileHandler(filename='app.log',encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.handlers = []
    logger.addHandler(file_handler)

    return logger

