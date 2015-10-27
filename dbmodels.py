""" GLOBAL IMPORTS """
import bcrypt


""" LOCAL IMPORTS """
import db

# [Ben-G] TODO: I create separate files for the User and Trip model

class UserModel(db.Model):
  """
  ' PURPOSE
  '   Contains data for all users
  """

  """ PROPERTIES """
  email = db.StringProperty()
  password = db.ByteStringProperty()

  """ CONSTANTS """
  # [Ben-G] TODO: It would be greate if this were a property of your
  # application that way your tests can access and modify the bcrypt rounds.
  # You want tests to run blazingly fast so you should set the rounds to the
  # minimum possible of 8.
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
    # [Ben-G] TODO: Minor note: you shoudn't need to implement this method
    # yourself. You should be able to use the `__dict__` method or other
    # python metaprogramming tools to generate the dictionary automatically
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
    # [Ben-G] TODO: Minor note: you shoudn't need to implement this method
    # yourself. You should be able to use the `__dict__` method or other
    # python metaprogramming tools to generate the dictionary automatically
    return {
      'name': self.name,
      'author': self.author.id
    }
