from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Resource, Api
from utils.mongo_json_encoder import JSONEncoder




app = Flask(__name__)
api = Api(app)




import db





def parameters(*params):
  def decorator(f):
    def scraper(*args, **kwargs):
      body = request.json
      for param in params:
        if not param in body: return abort(422)
        kwargs[param] = body[param]
      return f(*args, **kwargs)
    return scraper
  return decorator



# ORM


class UserModel(db.Model):
  
  email = db.StringProperty()
  password = db.ByteStringProperty()
  
  BCRYPT_ROUNDS = 12
  
  def hash_password(self, password):
    import bcrypt
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(self.BCRYPT_ROUNDS))
    return hashed
  
  def set_password(self, password):
    self.password = self.hash_password(password)
  
  def check_password(self, password):
    return self.password == self.hash_password(password)
  
  def to_dict(self):
    return {
      'email': self.email
    }
    




class TripModel(db.Model):
  
  # waypoints = ndb.ArrayProperty()
  name = db.StringProperty()
  author = db.KeyProperty()
  
  def to_dict(self):
    return {
      'name': self.name,
      'author': self.author.id
    }








class Users(Resource):
  
  @parameters('email', 'password')
  def post(self, email=None, password=None):
    trip = UserModel(email=email)
    trip.set_password(password)
    trip.save()
    return { 'id': trip.key.id }


class SpecificUser(Resource):
  
  def get(self, id):
    entity = UserModel.get_by_id(id)
    if not entity: return abort(400)
    return entity.to_dict()


class Trips(Resource):

  @parameters('name', 'author')
  def post(self, name=None, author=None):
    author_key = UserModel.key_from_id(author)
    trip = TripModel(name=name, author=author_key).save()
    return { 'id': trip.key.id }
  
  def get(self):
    entities = TripModel.fetch()
    return [entity.to_dict() for entity in entities]
  
  # returns amount of deleted
  def delete(self):
    deleted = TripModel.delete_all()
    return { 'deleted': deleted }


class SpecificTrip(Resource):
  
  def put(self, id):
    # TODO
    pass
  
  # returns amount of deleted
  def delete(self, id):
    key = TripModel.key_from_id(id)
    deleted = key.delete()
    return { 'deleted': deleted }
  
  def get(self, id):
    entity = TripModel.get_by_id(id)
    if not entity: return abort(400)
    return entity.to_dict()





# Add REST resource to API
api.add_resource(Trips, '/trips/')
api.add_resource(SpecificTrip, '/trips/<string:id>/')

api.add_resource(Users, '/users/')
api.add_resource(SpecificUser, '/users/<string:id>/')




# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp




if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(port=8080, debug=True)
