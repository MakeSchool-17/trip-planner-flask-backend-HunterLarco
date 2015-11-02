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
def auth(f):
  """
  ' PURPOSE
  '   Forces a given request to contain a valid Basic Authorization
  '   header using the UserModel as the auth database check.
  ' NOTES
  '   1. Adds an additional kwarg ( current_user ) which contains the
  '      entity of the current user based on the Basic Auth.
  """
  def handle(*args, **kwargs):
    basic = request.authorization
    if not basic: return abort(401)
    
    email = basic.username
    password = basic.password
    
    users = UserModel.fetch(UserModel.email == email)
    if len(users) == 0: return abort(401)
    
    user = users[0]
    if not user.check_password(password): return abort(401)
    
    kwargs['current_user'] = user
    
    return f(*args, **kwargs)
  return handle

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
  '   Contains methods that pertain to the entire user database
  '   as well as specific users via the auth decorator.
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
  
  @auth
  def get(self, current_user=None):
    """
    ' PURPOSE
    '   Return a dict representing the current user's public data.
    ' PARAMETERS
    '   optional <UserModel current_user>
    ' RETURNS
    '   dict *see the UserModel for specs*
    """
    return current_user.to_dict()


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
    entities = TripModel.query()
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
