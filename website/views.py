from flask import Blueprint, render_template, request,url_for, redirect,session, flash
from flask_login import current_user, login_required

#defines views blueprint
views = Blueprint('views', __name__)

@views.route('/')
def home():
  user = current_user
  return render_template("home.html",user=user)