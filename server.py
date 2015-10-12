from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from utils.mongo_json_encoder import JSONEncoder
from functools import wraps




# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)




#Implement REST Resource
class User(Resource):

  # @requires_auth
  def post(self):
    json = request.json
    collection = app.db.users
    addition = collection.insert_one(json)

    entity = collection.find_one({"_id": ObjectId(addition.inserted_id)})
    return entity

  def get(self, user_id):
    collection = app.db.users
    
    try:
      entity = collection.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
      response = jsonify(data=[])
      response.status_code = 404
      return response
      

    if not entity:
      response = jsonify(data=[])
      response.status_code = 404
      return response
    else:
      return entity





# Add REST resource to API
api.add_resource(User, '/users', '/users/', '/users/<string:user_id>')




# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp




if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
