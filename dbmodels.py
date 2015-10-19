""" LOCAL IMPORTS """
import db


class UserModel(db.Model):
  """
  ' PURPOSE
  '   Contains data for all users
  """
  
  """ PROPERTIES """
  email = db.StringProperty()
  password = db.ByteStringProperty()
  
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
    import bcrypt
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
    

class TripModel(db.Model):
  """
  ' PURPOSE
  '   Contains data for all trips
  """
  
  """ PROPERTIES """
  name = db.StringProperty()
  author = db.KeyProperty()
  
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
      'author': self.author.id
    }