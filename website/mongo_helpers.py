from pymongo import MongoClient
import os


mongo_username = os.environ["mongo_username"]
mongo_pw = os.environ["mongo_pw"]
db_url = f"mongodb+srv://{mongo_username}:{mongo_pw}@uni-meetups-data.8jmt1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"


def add_user(email,user_data):
  client = MongoClient(db_url)
  db = client["users"]
  users = db["users"]
  post = {"_id":email}
  for data in user_data:
    post[data] = user_data[data]
  
  users.insert_one(post)
  client.close()
  

def find_user(email):
  client = MongoClient(db_url)
  db = client["users"]
  users = db["users"]
  post = {"_id":email}
  
  return users.find_one(post)
  

def delete_user(email):
  client = MongoClient(db_url)
  db = client["users"]
  users = db["users"]
  post = {"_id":email}

  users.find_one_and_delete(post)
  client.close()
  
def update_user(email,field,value):
  client = MongoClient(db_url)
  db = client["users"]
  users = db["users"]
  post = {"_id":email}
  users.update_one(post,{"$set":{field:value}})
  client.close()

def get_schools():
  client = MongoClient(db_url)
  db = client["users"]
  schools = db["schools"]

  post = {}
  return schools.find(post)

def get_users():
  client = MongoClient(db_url)
  db = client["users"]
  users = db["users"]

  post = {}
  return users.find(post)

def add_meetup(school, field, value):
  client = MongoClient(db_url)
  db = client["users"]
  meetups = db["public_meetups"]

  post = {"_id": school}

  meetups.update_one(post, {"$set":{field:value}})
  client.close()

def find_meetups(school):
  client = MongoClient(db_url)
  db = client["users"]
  meetups = db["public_meetups"]

  post = {"_id": school}

  return meetups.find_one(post)

def update_meetups(school,meetup_data):
  client = MongoClient(db_url)
  db = client["users"]
  meetups = db["public_meetups"]
  post = {"_id": school}
  meetups.update_one(post,{"$set":{"meetups":meetup_data}})
  client.close()
