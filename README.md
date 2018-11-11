# interview-calendar

A repository with exercise code for an interview at a company that will remain unnamed.
Since this repository can't be private, and I don't want to make it easy for future candidates to copy-paste code,
the instructions here will remain vague enough as to be unsearchable. Sorry!

## Requirements
  * The API web interface is provided using Flask and Flask-restful.
  * The database backend is currently implemented with SQLite.

## Running from the command line
The API can be accessed directly from the command line, or via web.
To run the API from the command line, run `calendar_cli.py` with one of the following options:

  * `--add_user <user_id> <full name>` adds a user to the database
  * `--add_slot <user_id> <from> <to>` adds a slot to the selected user
  * `--see_slots <user_id>` shows all slots for a user
  * `--meeting <user_id> <user_id> ...` calculates a meeting across the given users

Dates are expected and returned in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

## Sending requests to the API

For simple GET requests, you can access the server via your browser. Simply start the flask server with the command:

``python flask_server.py``

and navigate to `http://localhost:5000` with one of the following endpoints:

  * `/person/<user_id>` returns information about a given user
  * `/slots/<user_id>` returns the available slots of a given user
  * `/meeting/<user_1>,<user_2>,...` returns the possible times for a meeting with the comma-separated
    list of participants

To send information to the API, you can use `curl`:
  * to add a new person to the database: `curl `
    `curl --data "name=Test user" http://localhost:5000/person/<user_id>`
  * to add a series of slots to a person:
    `curl --data "from=2018-12-12T14:00:00" --data "to=2018-12-12T16:00:00" http://localhost:5000/slots/<user_id>`

## License
This code is released under the JSON License.
