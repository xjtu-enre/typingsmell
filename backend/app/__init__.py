from flask import Flask
from flask_cors import CORS
from app.basic import Config, set_logger
from app.controllers import register_router
from app.daos import connect_db
from app.middlewares import log_middleware


def create_new_app() -> Flask:
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    CORS(app, supports_credentials=True)

    # 加载配置文件
    Config.set_config(app)

    # 配置 logger
    set_logger(app)

    # 请求日志
    log_middleware(app)

    # 注册路由
    register_router(app)

    # 连接数据库
    connect_db(app)

    app.logger.info('app 配置成功')
    return app
