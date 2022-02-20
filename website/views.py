from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required
from replit import db
from website.misc import get_matches

#defines views blueprint
views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
  if request.method == "POST":
    user = current_user
    match_email = request.form.get("meetup")
    match_name = db["users"][match_email]["full_name"]
    meetups_emails = []
    for meetup in db["users"][match_email]["meetups"]:
      keys = list(meetup.keys())
      meetups_emails.append(keys[0])

    print(meetups_emails)
    print(match_email)
    if match_email not in meetups_emails:
      print("Hi")
      db["users"][user.id]["meetups"].append({
      match_email:False
    })
      flash(f"A request to meet was sent to {match_name}.","yes")
      return redirect(url_for("views.home"))
    else:
      flash("You have already request to meet this person!","caution")
      return redirect(url_for("views.home"))
    
    
  
  else:
    user = current_user
    data = db["users"][user.id]
    print(data["profile_photo"])
    pfp = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
    desc = data["description"]
    school = data["school"]
    name = data["full_name"]
    matches = get_matches(user)
  
    return render_template("home.html",user=user,user_pic=pfp,user_name=name,desc=desc,matches=matches,school=school)
    