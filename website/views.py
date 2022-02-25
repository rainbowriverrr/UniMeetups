from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required
from website.misc import get_matches
import copy
import smtplib
import os
from collections import defaultdict,Counter
import json
from website.mongo_helpers import *

#defines views blueprint
views = Blueprint('views', __name__)

@views.route("/stats",methods=["GET"])
def show_stats():
  all_users = get_users()
  total_users = len(all_users)
  all_schools = get_schools()
  total_schools = len(all_schools)

  tags_by_school = defaultdict(list)

  for user in all_users:
    user_tags = all_users[user]["tags"]
    user_school = all_users[user]["school"]
    for tag in user_tags:
      tags_by_school[user_school].append(tag)

  tag_counts_by_school = {school : dict(Counter(tags_by_school[school])) for school in tags_by_school}

  response = {
    "total_users":total_users,
    "total_schools":total_schools,
    "tag_popularity_by_school":tag_counts_by_school
  }
  return json.dumps(response)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
  if request.method == "POST":
    user = current_user
    match_email = request.form.get("meetup_request")
    user_data = find_user(user.id)
    match_name = user_data["full_name"]
    meetup_requests = user_data["requests"]
    
    if user.id not in meetup_requests:
      user_data["requests"].append(user.id)
      update_user(user.id, "requests", user_data["requests"])
      flash(f"A request to meet was sent to {match_name}.","yes")
      return redirect(url_for("views.home"))
    else:
      flash("You have already request to meet this person!","caution")
      return redirect(url_for("views.home"))
    
    
  
  else:
    user = current_user
    user_data = find_user(user.id)
    pfp = url_for("static", filename=f"{user_data['profile_photo'].replace('website/static/','')}")
    desc = user_data["description"]
    school = user_data["school"]
    name = user_data["full_name"]
    matches = get_matches(user)
  
    return render_template("home.html",user=user,user_pic=pfp,user_name=name,desc=desc,matches=matches,school=school)


@views.route("/mail",methods=["GET","POST"])
@login_required
def send_mail():
  if request.method == "POST":
    mail = request.args.get("recepient")
    recp_data = find_user(mail)
    recp_name = recp_data["full_name"]
    user = current_user
    user_data = find_user(user.id)
    this_user_fullname = user_data['full_name']
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
    recp_data = find_user(mail)
    name = recp_data["full_name"]
    return render_template("send_mail.html",user=current_user,name=name)


@views.route("/createmeetup",methods=["POST","GET"])
@login_required
def display_create_meetup():
  if request.method == "POST":
    user = current_user
    cur_user = find_user(user.id)
    school = cur_user["school"]
    event_name = request.form.get("event_name")
    description = request.form.get("description")

    meta_data = {
      "name":event_name,
      "description":description,
      "people":[],
      "num_people":0,
      "event_organizer":user.id
    }
    meetups_data = find_meetups(school)
    meetups_data["meetups"].append(meta_data)
    update_meetups(school, meetups_data)
    
    flash("The following public meetup was created successfully!","ok")
    return redirect(url_for("views.display_meetups"))
    
  else:
    user = current_user
    cur_user = find_user(user.id)
    school = cur_user["school"]
    return render_template("create_meetup.html",user=current_user,school=school)

@views.route("/meetups",methods=["POST","GET"])
@login_required
def display_meetups():
  if request.method == "POST":
    user = current_user
    user_data = find_user(user.id)
    school = user_data["school"]
    if "create_meetup" in request.form:
      return redirect(url_for("views.display_create_meetup"))
    elif "end_meetup" in request.form:
      meetup_name = request.form["end_meetup"]
      meetups_data = find_meetups(school)
      meetups = meetups_data["meetups"]
      meetups = [metadata for metadata in meetups if metadata["name"] != meetup_name]
      update_meetups(school, meetup_data)
      flash("Successfully ended the event!","yes")
      return redirect(url_for("views.display_meetups"))
    elif "join_meetup" in request.form:
      meetup_name = request.form["join_meetup"]
      meetups_data = find_meetups(school)
      meetup_data = [metadata for metadata in meetups_data if metadata["name"]==meetup_name][0]
      joined = meetup_data["people"]
      
      if user.id not in joined:
        joined.append(user.id)
        meetup_data["num_people"]+=1
        update_meetups(school, meetup_data)
        flash(f"You have joined {meetup_name} successfully!","yes")
        return redirect(url_for("views.display_meetups"))
      else:
        flash(f"You already have joined {meetup_name} successfully!","error")
        return redirect(url_for("views.display_meetups"))
      
  else:
    user = current_user
    user_data = find_user(user.id)
    school = user_data["school"]
    school_meetup_data = find_meetups(school)
    
    meetups = school_meetup_data["meetups"]
    print(meetups)
    
    return render_template("meetups.html",user=current_user,school=school,meetups=meetups)

@views.route("/classmates",methods=["GET","POST"])
@login_required
def display_classmates():
  if request.method == "POST":
    mail = request.form.get("mail")
    return redirect(url_for("views.send_mail",recepient=mail))
  else:
    user = current_user
    user_data = find_user(user.id)
    user_classmates = user_data["classmates"]
    user_school = user_data["school"]
    classmates = []

    for classmate in user_classmates:
      classmate_data = find_user(classmate)
      data = copy.deepcopy(classmate_data)
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
    user_data = find_user(user.id)
    
    if "accept" in form_data:
      match_email = form_data.get("accept")
      match_data = find_user(match_email)
      user_data["requests"].remove(match_email)
      
      
      user_data["classmates"].append(match_email)
      match_data["classmates"].append(user.id)
      user_data["classmates"] = list(set(user_data["classmates"]))
      match_data["classmates"] = list(set(match_data["classmates"]))

      update_user(user.id,"requests",user_data["requests"])
      update_user(user.id,"classmates",user_data["classmates"])
      update_user(match_email,"classmates",match_data["classmates"])
      
      return redirect(url_for("views.display_requests"))
    elif "decline" in form_data:
      match_email = form_data.get("decline")
      user_data["requests"].remove(match_email)

      update_user(user.id,"requests",user_data["requests"])
      
      return redirect(url_for("views.display_requests"))
          
  else:
    meetup_requests = []
    user = current_user
    user_data = find_user(user.id)

    for email in user_data["requests"]:
      req_user_data = find_user(email)
      data = copy.deepcopy(req_user_data)
      data["profile_photo"] = url_for("static", filename=f"{data['profile_photo'].replace('website/static/','')}")
      meetup_requests.append(data)
    
    
    return render_template("requests.html",user=current_user,meetup_requests=meetup_requests)

@views.route("/about")
def about():
  all_users = [user for user in get_users()]
  all_schools = [school for school in get_schools()]
  num_users = len(all_users)
  num_schools = len(all_schools)
  tanish_pic = url_for("static",filename="team_photos/tanish.jpg")
  tony_pic = url_for("static",filename="team_photos/tony.jpg")
  river_pic = url_for("static",filename="team_photos/river.jpg")

  return render_template("about.html",user=current_user,num_users=num_users,num_schools=num_schools,tanish_pic=tanish_pic,tony_pic=tony_pic,river_pic=river_pic)
  

  
  