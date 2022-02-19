from flask import Blueprint, render_template, request,url_for, redirect

import random
import json
from website.location_handling import distance

#defines views blueprint
views = Blueprint('views', __name__)







@views.route('/')
def home():
  return render_template("home.html")