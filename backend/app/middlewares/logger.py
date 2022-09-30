from flask import Flask, request, Response


def log_middleware(app: Flask):
    @app.before_request
    def before_log():
        app.logger.info({
            'url': request.url,
            'method': request.method,
            'body': request.json,
        })

    @app.after_request
    def after_log(response: Response):
        app.logger.info({
            'status': response.status_code,
            'body': response.json,
            'header': response.headers
        })
        return response
