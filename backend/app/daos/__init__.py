from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()


def connect_db(app: Flask):
    try:
        db.init_app(app)
        app.logger.info('成功连接数据库')
    except BaseException as e:
        app.logger.error('连接数据库失败', e)


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
