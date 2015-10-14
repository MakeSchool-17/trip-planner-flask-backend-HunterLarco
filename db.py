import base64

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

mongo = MongoClient('localhost', 27017)
rawdb = mongo.develop_database



# do not use this class
class Property(object):
  def unpack(self, value):
    return value
  
  def pack(self, value):
    return value

class JsonProperty(Property):
  pass

class KeyProperty(Property):
  def unpack(self, value):
    if value == None: return None
    from db import Key
    return Key(serial=value)
  
  def pack(self, value):
    if value == None: return None
    from db import Key
    if not isinstance(value, Key):
      raise ValueError('KeyProperty must contain Key instance')
    return value.serialize()





class Key(object):
  
  def __init__(self, model=None, id=None, urlsafe=None, serial=None):
    if serial:
      try:
        modelname, self.id = tuple(serial.split(':'))
      except:
        raise ValueError('Malformed serialized key')
      
      models = Model.__subclasses__()
      models.reverse()
      for model in models:
        if modelname == model.__name__:
          self.model = model
          break
      else:
        raise ValueError('Invalid serial key model')
    elif urlsafe:
      try:
        decoded = base64.b64decode(urlsafe).decode('utf-8') 
        modelname, self.id = tuple(decoded.split(':'))
      except:
        raise ValueError('Malformed urlsafe key')
      
      models = Model.__subclasses__()
      models.reverse()
      for model in models:
        if modelname == model.__name__:
          self.model = model
          break
      else:
        raise ValueError('Invalid urlsafe key model')
    elif model and id:
      self.model, self.id = (model, id)
    else:
      raise ValueError('Expected model and id or urlsafe')
  
  def serialize(self):
    return '%s:%s' % (self.model.__name__, self.id)
  
  def urlsafe(self):
    base_string = self.serialize()
    encoded = base64.b64encode(bytes(base_string, 'utf8'))
    formatted = encoded.decode('utf-8') 
    return formatted
  
  def delete(self):
    collection = getattr(rawdb, self.model.__name__)
    collection.remove({ '_id': ObjectId(self.id) })
  
  def get(self):
    try:
      return self.model(key=self)
    except:
      return None
  
  def __repr__(self):
    return '<db.Key %s>' % self.serialize()
  
  def __str__(self):
    return '<db.Key %s>' % self.serialize()




class Model(object):
  
  @classmethod
  def key_from_id(cls, id):
    return Key(cls, id)
  
  
  def __init__(self, key=None, id=None):
    
    self._properties = []
    for attr in vars(self.__class__):
      val = getattr(self.__class__, attr)
      if isinstance(val, Property):
        self._properties.append(attr)
        setattr(self, attr, None)
    
    if key:
      self.key = key
    elif id:
      self.key = self.key_from_id(id)
    else:
      self.key = None
    
    self.__load__()
  
  
  def __json__(self):
    json = {}
    for attr in self._properties:
      packer = getattr(self.__class__, attr)
      json[attr] = packer.pack(getattr(self, attr))
    return json
  
  
  def __load__(self):
    if not self.key: return
    
    collection = getattr(rawdb, self.__class__.__name__)
    entity = collection.find_one({'_id': ObjectId(self.key.id)})
    if not entity:
      raise ValueError('Entity does not exist')
    
    reserved = ['_id']
    for key, value in entity.items():
      if not key in reserved:
        packer = getattr(self.__class__, key)
        setattr(self, key, packer.unpack(value))
  
  
  def put(self):
    collection = getattr(rawdb, self.__class__.__name__)
    saved = collection.insert_one(self.__json__())
    id = saved.inserted_id
    self.key = Key(self.__class__, id)
  
  
  def delete(self):
    self.key.delete()



