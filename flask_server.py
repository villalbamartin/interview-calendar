#!/usr/bin/python3

import dateutil.parser
from backend import Calendar
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
DATABASE = 'database.db'


class People(Resource):
    def get(self, user_id):
        cal = Calendar(DATABASE)
        retval = cal.get_user(user_id)
        return retval

    def post(self, user_id):
        cal = Calendar(DATABASE)
        name = request.form.get('name')
        return cal.add_user(user_id, name)


class Slots(Resource):
    def get(self, user_id):
        cal = Calendar(DATABASE)
        retval = cal.get_slots(user_id)
        return retval

    def post(self, user_id):
        cal = Calendar(DATABASE)
        date_from = request.form.get('from')
        date_to = request.form.get('to')
        return cal.add_slots(user_id,
                             dateutil.parser.parse(date_from),
                             dateutil.parser.parse(date_to))


class Meeting(Resource):
    def get(self, user_ids):
        cal = Calendar(DATABASE)
        users = user_ids.split(',')
        retval = cal.organize_meeting(users[0], users[1:])
        return retval


api.add_resource(People, '/people/<user_id>')
api.add_resource(Slots, '/slots/<user_id>')
api.add_resource(Meeting, '/meeting/<user_ids>')

if __name__ == '__main__':
    app.run(port='5000')
