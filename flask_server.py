#!/usr/bin/python3
from flask import Flask, request

# To run: FLASK_APP=flask_server.py python3 -m flask run --host=0.0.0.0
app = Flask(__name__)

@app.route("/")
def serve():
    param = request.args.get('request')
    return param
