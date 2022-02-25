from flask_login import UserMixin
from website.mongo_helpers import find_user

class User(UserMixin):
  def __init__(self,id):
    self.json_data = find_user(id)
    self.id = self.json_data["email"]
    self.school = self.json_data["school"]
    self.tags = self.json_data["tags"]
    self.pfp_source = self.json_data["profile_photo"]
    self.description = self.json_data["description"]
    self.authenticated = False
  
  def is_active(self):
    return True

  def get_id(self):
    return self.id

  def is_authenticated(self):
    """Return True if the user is authenticated."""
    return self.authenticated

  def is_anonymous(self):
      return False

