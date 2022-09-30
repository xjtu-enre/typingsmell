from flask import Flask

from app.controllers.ping import ping
from app.controllers.upload import proj_upload
from app.controllers.import_project import import_project
from app.controllers.ctr_project import ctr_project
from app.controllers.ctr_coverage import ctr_coverage
from app.controllers.ctr_usage import ctr_usage
from app.controllers.ctr_pattern import ctr_pattern
from app.controllers.ctr_file import ctr_file
from app.controllers.ctr_recommend import ctr_recommend


def register_router(app: Flask):
    # ping
    app.register_blueprint(ping)
    # upload
    app.register_blueprint(proj_upload)
    # fetch
    app.register_blueprint(import_project)
    # coverage
    app.register_blueprint(ctr_coverage)
    # project
    app.register_blueprint(ctr_project)
    # usage
    app.register_blueprint(ctr_usage)
    # pattern
    app.register_blueprint(ctr_pattern)
    # project
    app.register_blueprint(ctr_file)
    # recommend
    app.register_blueprint(ctr_recommend)
