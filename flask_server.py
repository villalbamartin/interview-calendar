#!/usr/bin/python3

import dateutil.parser
from backend import Calendar
from flask import Flask, request
from flask_restful import Resource, Api


# To run: FLASK_APP=flask_server.py python3 -m flask run --host=0.0.0.0
app = Flask(__name__)
api = Api(app)
cal = Calendar('database.db')

class Person(Resource):
    def post(self, user_id):
        name = request.form.get('name')
        return cal.add_user(user_id, name)


class Slots(Resource):
    def get(self, user_id):
        retval = cal.get_slots(user_id)
        return retval

    def post(self, user_id):
        date_from = request.form.get('from')
        date_to = request.form.get('to')
        return cal.add_slots(user_id,
                             dateutil.parser.parse(date_from),
                             dateutil.parser.parse(date_to))


class Meeting(Resource):
    def get(self, user_ids):
        users = user_ids.split(',')
        retval = cal.organize_meeting(users[0], users[1:])
        return retval


api.add_resource(Person, '/person/<user_id>')
api.add_resource(Slots, '/slots/<user_id>')
api.add_resource(Meeting, '/meeting/<user_ids>')

if __name__ == '__main__':
    app.run(port='5000')
