""" GLOBAL IMPORTS """
import bcrypt


""" LOCAL IMPORTS """
import TableMongo as db


class UserModel(db.Model):
  """
  ' PURPOSE
  '   Contains data for all users
  """
  
  """ PROPERTIES """
  email = db.StringProperty(required=True)
  password = db.ByteStringProperty(required=True)
  
  """ CONSTANTS """
  BCRYPT_ROUNDS = 12
  
  def hash_password(self, password):
    """
    ' PURPOSE
    '   Given a password, hash that password using bcrypt
    ' PARAMETERS
    '   <str password>
    ' RETURNS
    '   <bytes hashed>
    """
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(self.BCRYPT_ROUNDS))
    return hashed
  
  def set_password(self, password):
    """
    ' PURPOSE
    '   Given a password, alters the model's password
    '   field to contain the new password after being
    '   hashed.
    ' PARAMETERS
    '   <str password>
    ' RETURNS
    '   Nothing
    """
    self.password = self.hash_password(password)
  
  def check_password(self, password):
    """
    ' PURPOSE
    '   Given a password, verifies that it is the same
    '   password that is contained by this model.
    ' PARAMETERS
    '   <str password>
    ' RETURNS
    '   True if the passwords match
    '   False if th passwords do not match
    """
    password = password.encode('utf-8')
    return bcrypt.hashpw(password, self.password) == self.password
  
  def to_dict(self):
    """
    ' PURPOSE
    '   Returns a public dict of this model
    ' PARAMETERS
    '   None
    ' RETURNS
    '   dict( email )
    '     email -> the user's email
    """
    return {
      'email': self.email
    }


class Coordinate(object):
  
  def __init__(self, x=0, y=0):
    self.x = 0
    self.y = 0
  
  def __repr__(self):
    return self.__str__()
  
  def __str__(self):
    return 'Coordinate(x=%s, y=%s)' % (self.x, self.y)

    
class CoordinateProperty(db.Property):
  
  @staticmethod
  def type():
    return Coordinate
  
  def pack(self, value):
    return [value.x, value.y]
  
  def unpack(self, value):
    return Coordinate(value[0], value[1])


class TripModel(db.Model):
  """
  ' PURPOSE
  '   Contains data for all trips
  """
  
  """ PROPERTIES """
  name = db.StringProperty(required=True)
  author = db.KeyProperty(required=True)
  waypoints = CoordinateProperty(multiple=True, default=[])
  
  def to_dict(self):
    """
    ' PURPOSE
    '   Returns a public dict of this model
    ' PARAMETERS
    '   None
    ' RETURNS
    '   dict( name, author )
    '     name -> the name of this trip
    '     author -> the identifier of the author of this trip
    """
    return {
      'name': self.name,
      'author': self.author.id,
      'waypoints': [{'x': waypoint.x, 'y': waypoint.y} for waypoint in self.waypoints]
    }
