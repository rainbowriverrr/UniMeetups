from replit import db
from website.user import User
from flask import url_for
import copy
from website.mongo_helpers import get_users


UPLOAD_PATH = "website/static/profile_photos"

def get_tags():
  with open("website/tags.txt","r") as file:
    tags = file.read().splitlines()
    
  return tags

def get_matches(user : User):
  all_users = [user for user in get_users()]
  main_school = user.school
  main_tags = user.tags
  main_email = user.id
  
  same_school = lambda target : target["school"] == main_school and target["email"] != user.id
  pool = list(filter(same_school,list(all_users)))
  
  potential_matches = []
  
  for person in pool:
    tags = person["tags"]
    cur_classmates = person["classmates"]
    
    proportion = len([tag for tag in tags if tag in main_tags]) / len(main_tags)
    if proportion >= 0.65 and user.id not in cur_classmates:
      copied_data = copy.deepcopy(person)
      copied_data["profile_photo"] = url_for('static',filename= copied_data["profile_photo"].replace('website/static/',''))
      potential_matches.append(copied_data)
      
  return potential_matches
  
    
    


  

  
  