from flask_login import UserMixin
from replit import db

class User(UserMixin):
  def __init__(self,id):
    self.json_data = db["users"][id]
    self.id = self.json_data["email"]
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
