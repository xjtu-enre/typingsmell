import logging
import pathlib

from flask import Flask
from logging.handlers import TimedRotatingFileHandler


def set_logger(app: Flask):
    path = pathlib.Path(__file__).parent.parent.parent
    path = pathlib.Path.joinpath(path, 'log', 'flask.log')

    handler = TimedRotatingFileHandler(
        path, when='D', interval=1, backupCount=15,
        encoding='UTF-8', delay=False, utc=False
    )

    formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')

    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(level=app.config['LEVEL'])
