import requests


class MyRequest:
    BASE_URL = "http://127.0.0.1:9000/"

    @classmethod
    def post_remote_server(cls, url, image):
        return requests.post(MyRequest.BASE_URL + url, json={'img': image})
