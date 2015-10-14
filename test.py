import db
import server




class Test(db.Model):
  
  value1 = db.JsonProperty()
  value2 = db.JsonProperty()




def TestKeysandIds():
  entity = Test()
  entity.value1 = 'Test'
  entity.put()
  print(entity)

  print(entity.__json__())
  print(entity.value1)
  print(Test.value1)

  print(entity.key)

  urlsafe = entity.key.urlsafe()
  print(urlsafe)

  key = db.Key(urlsafe=urlsafe)
  print(key)

  entity = key.get()
  print(entity)

  print(entity.__json__())
  print(entity.value1)
  print(Test.value1)


  class Test(db.Model):
  
    value1 = db.Property()
    value2 = db.Property()
    value3 = db.Property()


  print(db.Model.__subclasses__())

  entity = Test(id=key.id)
  print(entity)

  print(entity.__json__())
  print(entity.value3)


  print(key.serialize())
  entity = db.Key(serial=key.serialize()).get()
  print(entity)
  print(entity.__json__())

  entity.delete()

  entity = Test(id=key.id)
  print(entity)
  print(entity.__json__())
  


class Reference(db.Model):
  value1 = db.Property()
  value2 = db.Property()
  other = db.KeyProperty()


def TestPropertyPacking():
  
  entity = Reference()
  entity.value1 = 'E1V1'
  entity.value2 = True
  entity.put()
  
  print('First Entity Key   : %s' % entity.key)
  
  entity2 = Reference()
  entity2.value1 = 'E2V1'
  entity2.value2 = False
  entity2.other = entity.key
  entity2.put()

  print('Second Entity Key  : %s' % entity2.key)
  
  print('First Entity JSON  : %s' % entity.__json__())
  print('Second Entity JSON : %s' % entity2.__json__())




if __name__ == '__main__':
  # TestKeysandIds()
  TestPropertyPacking()
  
  