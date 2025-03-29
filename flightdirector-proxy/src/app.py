from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

TARGET_URL = "https://flightdirector.de"

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    auth = (os.getenv("FD_USERNAME"), os.getenv("FD_PASSWORD"))
    url = f"{TARGET_URL}/{path}"
    resp = requests.get(url, auth=auth, headers={key: value for (key, value) in request.headers if key.lower() != 'host'}, stream=True)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    return Response(resp.content, resp.status_code, headers)
