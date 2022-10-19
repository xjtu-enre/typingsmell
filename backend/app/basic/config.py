import os
import pathlib
import threading
import yaml

from flask import Flask


class Config:
    _config = None
    _instance_lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._config is None:
            with cls._instance_lock:
                # mode = os.environ.get('mode') if os.environ.get('mode') is not None else 'prod'
                mode = 'dev'
                path = pathlib.Path(__file__).parent.parent.parent
                path = pathlib.Path.joinpath(path, f'{mode}.yaml')

                with open(str(path), 'rb') as f:
                    config = yaml.safe_load(f.read())
                    cls._config = config

        return cls._config

    @classmethod
    def set_config(cls, app: Flask):
        app.config.update(cls.get_instance())
