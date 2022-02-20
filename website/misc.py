from replit import db
from website.user import User
from flask import url_for
import copy

UPLOAD_PATH = "website/static/profile_photos"

def get_tags():
  with open("website/tags.txt","r") as file:
    tags = file.read().splitlines()
    
  return tags

def get_matches(user : User):
  all_users = db["users"]
  main_school = user.school
  main_tags = user.tags

  
  same_school = lambda target : all_users[target]["school"] == main_school and target != user.id
  pool = set(list(filter(same_school,list(all_users.keys()))))
  potential_matches = []
  
  for person in pool:
    tags = all_users[person]["tags"]
    proportion = len([tag for tag in tags if tag in main_tags]) / len(main_tags)
    if proportion >= 0.65:
      copied_data = copy.deepcopy(all_users[person])
      copied_data["profile_photo"] = url_for('static',filename= copied_data["profile_photo"].replace('website/static/',''))
      potential_matches.append(copied_data)
      

  return potential_matches
  
    
    


  

  
  