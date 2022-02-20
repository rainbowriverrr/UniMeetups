from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required
from replit import db
from website.misc import get_matches
import copy
import smtplib
import os

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


@views.route("/mail",methods=["GET","POST"])
@login_required
def send_mail():
  if request.method == "POST":
    mail = request.args.get("recepient")
    recp_name = db["users"][mail]["full_name"]
    user = current_user
    this_user_fullname = db["users"][user.id]["full_name"]
    name_attach = f"This message was sent on the behalf of {this_user_fullname}."
    msg = f"{request.form.get('message')} \n {name_attach}"
    if len(msg) == 0:
      flash("The message field cannot be empty, please try to send your message again!","error")
      return redirect(url_for("views.send_mail",recepient=mail))
    
    email_session = smtplib.SMTP("smtp.gmail.com",587)
    email_session.starttls()
    username,pw = os.environ["bot_email"],os.environ["bot_pw"]
    print(username,pw)
    email_session.login(username,pw)
    try:
      email_session.sendmail(username, mail,msg)
      flash(f"The message was sent to {recp_name}!","yes")
      return redirect(url_for("views.display_classmates"))
    except:
      flash(f"There was an error in sending the message to {recp_name}, please try again later!","error")
      return redirect(url_for("views.send_mail",recepient=mail))
      
      
    
  
  else:
    mail = request.args.get("recepient")
    name = db["users"][mail]["full_name"]
    return render_template("send_mail.html",user=current_user,name=name)


@views.route("/createmeetup",methods=["POST","GET"])
@login_required
def display_create_meetup():
  if request.method == "POST":
    user = current_user
    school = db["users"][user.id]["school"]
    event_name = request.form.get("event_name")
    description = request.form.get("description")

    meta_data = {
      "description":description,
      "people":[],
      "num_people":0,
      "event_organizer":user.id
    }
    db["public_meetups"][school][event_name] = meta_data
    flash("The following public meetup was created successfully!","ok")
    return redirect(url_for("views.display_meetups"))
    
  else:
    user = current_user
    school = db["users"][user.id]["school"]
    return render_template("create_meetup.html",user=current_user,school=school)

@views.route("/meetups",methods=["POST","GET"])
@login_required
def display_meetups():
  if request.method == "POST":
    user = current_user
    school = db["users"][user.id]["school"]
    if "create_meetup" in request.form:
      return redirect(url_for("views.display_create_meetup"))
    elif "end_meetup" in request.form:
      meetup_name = request.form["end_meetup"]
      del db["public_meetups"][school][meetup_name]
      flash("Successfully ended the event!","yes")
      return redirect(url_for("views.display_meetups"))
    elif "join_meetup" in request.form:
      meetup_name = request.form["join_meetup"]
      meetup_data = db["public_meetups"][school][meetup_name]
      joined = meetup_data["people"]
      
      if user.id not in joined:
        joined.append(user.id)
        meetup_data["num_people"]+=1
        flash(f"You have joined {meetup_name} successfully!","yes")
        return redirect(url_for("views.display_meetups"))
      else:
        flash(f"You already have joined {meetup_name} successfully!","error")
        return redirect(url_for("views.display_meetups"))
      
  else:
    user = current_user
    school = db["users"][user.id]["school"]
    meetups = db["public_meetups"][school]
    
    return render_template("meetups.html",user=current_user,school=school,meetups=meetups)

@views.route("/classmates",methods=["GET","POST"])
@login_required
def display_classmates():
  if request.method == "POST":
    mail = request.form.get("mail")
    return redirect(url_for("views.send_mail",recepient=mail))
  else:
    user = current_user
    user_classmates = db["users"][user.id]["classmates"]
    user_school = db["users"][user.id]["school"]
    classmates = []

    for classmate in user_classmates:
      data = copy.deepcopy(db["users"][classmate])
      data["profile_photo"] = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
      if user_school == data["school"]:
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
      db["users"][match_email]["classmates"].append(user.id)
      db["users"][user.id]["classmates"] = list(set(db["users"][user.id]["classmates"]))
      db["users"][match_email]["classmates"] = list(set(db["users"][match_email]["classmates"]))
      
      return redirect(url_for("views.display_requests"))
    elif "decline" in form_data:
      match_email = form_data.get("decline")
      db["users"][user.id]["requests"].remove(user.id)
      return redirect(url_for("views.display_requests"))
          
  else:
    meetup_requests = []
    user = current_user

    for email in db["users"][user.id]["requests"]:
      data = copy.deepcopy(db["users"][email])
      data["profile_photo"] = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
      meetup_requests.append(data)
    
    
    return render_template("requests.html",user=current_user,meetup_requests=meetup_requests)

@views.route("/about")
def about():
  num_users = len(db["users"])
  num_schools = len(db["schools"])
  tanish_pic = url_for("static",filename="team_photos/tanish.jpg")
  tony_pic = url_for("static",filename="team_photos/tony.jpg")
  river_pic = url_for("static",filename="team_photos/river.jpg")

  return render_template("about.html",user=current_user,num_users=num_users,num_schools=num_schools,tanish_pic=tanish_pic,tony_pic=tony_pic,river_pic=river_pic)
  

  
  