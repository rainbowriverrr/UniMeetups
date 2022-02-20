from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required
from replit import db
from website.misc import get_matches
import copy

#defines views blueprint
views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
  if request.method == "POST":
    user = current_user
    match_email = request.form.get("meetup_request")
    match_name = db["users"][match_email]["full_name"]
    meetup_requests = db["users"][match_email]["requests"]
    classmates = db["users"][user.id]["classmates"]
    
    if user.id not in meetup_requests:
      db["users"][match_email]["requests"].append(user.id)
      
      flash(f"A request to meet was sent to {match_name}.","yes")
      return redirect(url_for("views.home"))
    else:
      flash("You have already request to meet this person!","caution")
      return redirect(url_for("views.home"))
    
    
  
  else:
    user = current_user
    data = db["users"][user.id]
    pfp = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
    desc = data["description"]
    school = data["school"]
    name = data["full_name"]
    matches = get_matches(user)
  
    return render_template("home.html",user=user,user_pic=pfp,user_name=name,desc=desc,matches=matches,school=school)


@views.route("/classmates",methods=["GET","POST"])
@login_required
def display_classmates():
  if request.method == "POST":
    pass
  else:
    user = current_user
    user_classmates = db["users"][user.id]["classmates"]
    classmates = []

    for classmate in user_classmates:
      data = copy.deepcopy(db["users"][classmate])
      if user.id in data["classmates"]:
        data["mutual_acceptance"] = True 
        classmates.append(data)
      else:
        data["mutual_acceptance"] = False
        del data["socials"]
        classmates.append(data)
    
    return render_template("classmates.html",user=current_user,classmates=classmates)

@views.route("/requests", methods = ['GET', 'POST'])
@login_required
def display_requests():
  if request.method == "POST":
    form_data = request.form
    user = current_user
    if "accept" in form_data:
      match_email = form_data.get("accept")
      db["users"][user.id]["requests"].remove(match_email)
      db["users"][user.id]["classmates"].append(match_email)
      return redirect(url_for("views.display_requests"))
    elif "decline" in form_data:
      match_email = form_data.get("decline")
      db["users"][user.id]["requests"].remove(match_email)
      return redirect(url_for("views.display_requests"))
          
  else:
    meetup_requests = []
    user = current_user

    for email in db["users"][user.id]["requests"]:
      data = copy.deepcopy(db["users"][email])
      data["profile_photo"] = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
      meetup_requests.append(data)
    
    
    return render_template("requests.html",user=current_user,meetup_requests=meetup_requests)