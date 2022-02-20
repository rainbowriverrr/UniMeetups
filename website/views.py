from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required
from replit import db
from website.misc import get_matches

#defines views blueprint
views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
  user = current_user
  data = db["users"][user.id]
  print(data["profile_photo"])
  pfp = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
  desc = data["description"]
  school = data["school"]
  name = data["full_name"]
  matches = get_matches(user)
  
  
  return render_template("home.html",user=user,user_pic=pfp,user_name=name,desc=desc,matches=matches,school=school)
  