#!/usr/bin/python3
import json
from backend import Calendar
from flask import Flask
from flask_restful import Resource, Api


# To run: FLASK_APP=flask_server.py python3 -m flask run --host=0.0.0.0
app = Flask(__name__)
api = Api(app)
cal = Calendar('database.db')


class Slots(Resource):
    def get(self, user_id):
        retval = cal.get_slots(user_id)
        return retval

api.add_resource(Slots, '/slots/<user_id>')

if __name__ == '__main__':
    app.run(port='5000')