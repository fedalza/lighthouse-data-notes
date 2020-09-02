from flask import Flask, jsonify

from flask_restful import Resource, Api, reqparse

# create an application
app = Flask(__name__)

# create an API for the application
api = Api(app)

# adding endpoint by creating class with name Greet
# this class will inherit properties from the Resources class from flask_restful
class Greet(Resource):
    def get(self):
        # create request parser
        parser = reqparse.RequestParser()

        # create argument 'name'
        parser.add_argument('name', type=str)

        # parse 'name'
        name = parser.parse_args().get('name')

        if name:
            greeting = f'Hello {name}!'
        else:
            greeting = 'Hello person without name!'

        # make json from greeting string
        return jsonify(greeting=greeting)

# The class Greet contains only one method – get. This time the naming convention is strict (we can use only HTTP request methods: get, post, put, ...). Inside the get method, we initialize RequestParser() which allows us to parse optional arguments. We create only one optional argument name as a string type. In the variable name, we store an argument value that was passed by calling our API. If the user doesn't pass the argument name in an API call the value of the variable is NULL. We also create different greetings based on the value in the name variable.

# assign endpoint
api.add_resource(Greet,'/greet')

# create application run when file is called directly
if __name__ == '__main__':
    app.run(debug=True)