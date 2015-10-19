""" FLASK IMPORTS """
from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Resource, Api


""" MONGO IMPORTS """
from utils.mongo_json_encoder import JSONEncoder


""" LOCAL IMPORTS """
from dbmodels import UserModel, TripModel


""" FLASK SETUP """
app = Flask(__name__)
api = Api(app)


""" DECORATORS """
def parameters(*params):
  """
  ' PURPOSE
  '   Given a list of parameters, grabs them from the request's
  '   body (assumed to be json) and then adds them to the intended
  '   kwargs. Essentially removing the boilerplate to get body
  '   fields.
  ' PARAMETERS
  '   <str field_name1>
  '   <str field_name2>
  '   ...
  '   <str field_nameN>
  ' RETURNS
  '   Runs the original function and returns the result.
  ' NOTES
  '   1. Will throw error code 422 if an expected parameter is not
  '      present in the request body.
  """
  def decorator(f):
    def scraper(*args, **kwargs):
      body = request.json
      for param in params:
        if not param in body: return abort(422)
        kwargs[param] = body[param]
      return f(*args, **kwargs)
    return scraper
  return decorator


""" RESTFUL API RESOURCES """
class Users(Resource):
  """
  ' PURPOSE
  '   Contains methods that pertain to the entire user database.
  '   No users are specified in any of the requests.
  """
  
  @parameters('email', 'password')
  def post(self, email=None, password=None):
    """
    ' PURPOSE
    '   Given and email and password, create a new user.
    '   Returns the new user's identifier
    ' PARAMETERS
    '   <str email>
    '   <str password>
    ' RETURNS
    '   dict( id )
    '     id -> the identifier of the created user
    """
    user = UserModel(email=email)
    user.set_password(password)
    user.save()
    return { 'id': user.key.id }


class SpecificUser(Resource):
  """
  ' PURPOSE
  '   Contains methods that pertain a specific user.
  """
  
  def get(self, id):
    """
    ' PURPOSE
    '   Given a user id, return a dict representing
    '   that user's public data.
    ' PARAMETERS
    '   <str id>
    ' RETURNS
    '   dict *see the UserModel for specs*
    """
    entity = UserModel.get_by_id(id)
    if not entity: return abort(400)
    return entity.to_dict()


class Trips(Resource):
  """
  ' PURPOSE
  '   Contains methods that pertain to the entire trip database.
  '   No trips are specified in any of the requests.
  """

  @parameters('name', 'author')
  def post(self, name=None, author=None):
    """
    ' PURPOSE
    '   Given a trip name and author identifier, create
    '   a new trip. Returns the identifier of the new trip.
    ' PARAMETERS
    '   <str name>
    '   <str author> identifier
    ' RETURNS
    '   dict( id )
    '     id -> the identifier of the created trip
    """
    author_key = UserModel.key_from_id(author)
    trip = TripModel(name=name, author=author_key).save()
    return { 'id': trip.key.id }
  
  def get(self):
    """
    ' PURPOSE
    '   Returns the public dicts for all trips.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   [<dict entity1>, ..., <dict entityN>]
    """
    entities = TripModel.fetch()
    return [entity.to_dict() for entity in entities]
  
  # returns amount of deleted
  def delete(self):
    """
    ' PURPOSE
    '   Deletes all existing trips
    ' PARAMETERS
    '   None
    ' RETURNS
    '   dict( deleted )
    '     deleted -> the count of deleted trips
    """
    deleted = TripModel.delete_all()
    return { 'deleted': deleted }


class SpecificTrip(Resource):
  """
  ' PURPOSE
  '   Contains methods that pertain a specific trip.
  """

  def delete(self, id):
    """
    ' PURPOSE
    '   Given a trip id, delete that trip.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   dict( deleted )
    '     deleted -> the count of deleted trips
    """
    key = TripModel.key_from_id(id)
    deleted = key.delete()
    return { 'deleted': deleted }
  
  def get(self, id):
    """
    ' PURPOSE
    '   Given a trip id, return a dict representing
    '   that trip's public data.
    ' PARAMETERS
    '   <str id>
    ' RETURNS
    '   dict *see the TripModel for specs*
    """
    entity = TripModel.get_by_id(id)
    if not entity: return abort(400)
    return entity.to_dict()


""" RESTFUL API RESOURCE ROUTING """
api.add_resource(Trips, '/trips/')
api.add_resource(SpecificTrip, '/trips/<string:id>/')

api.add_resource(Users, '/users/')
api.add_resource(SpecificUser, '/users/<string:id>/')


""" CUSTOM JSON SERIALIZER FOR flask_restful """
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp


""" START SERVER """
if __name__ == '__main__':
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(port=8080, debug=True)
