from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash #hash to store encrypted password
from flask_login import login_user, login_required, logout_user, current_user
from replit import db
from website.location_handling import get_closest_schools
from website.misc import get_tags

# define form constants for sign up
MINIMUM_EMAIL_LENGTH = 5
MINIMUM_FULL_NAME_LENGTH = 5
MAX_FORM_LENGTH = 95
MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 40

#defines auth blueprint view
auth = Blueprint('auth', __name__)

#login page (arg passed is the URL route to get to the page. It goes after master prefix)
#ie: if master prefix defined in init is /hi, then to get here we need /hi/login 
#GET: When go to URL from url bar, POST when submit button (send info)
@auth.route('/login', methods=['GET', 'POST']) #clarifies supported request types
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password1')

    #checks for any users in the database that match the email entered
    if db[email]:
      pass
      
        

    #access data sent via the form
    #data = request.form 
    #print(data)
  else:
    return render_template("login.html", user=current_user)

#logout page
@auth.route('/logout')
#@login_required #login needed to access this page
def logout():
    #logout_user()
    flash('Successfully logged out', category='no')
    return redirect(url_for('auth.login'))

#sign up page
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method =='POST':

        email = request.form.get('email')
        full_name = request.form.get('name')
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')

        
        #No. 1: Name field must not be empty
        if len(full_name) not in range(MINIMUM_FULL_NAME_LENGTH, MAX_FORM_LENGTH+1):
            flash(f'Name must be between {MINIMUM_FULL_NAME_LENGTH} and {MAX_FORM_LENGTH} characters', category='error')

        #No. 2: Email field must not be empty
        elif len(email) not in range(MINIMUM_EMAIL_LENGTH, MAX_FORM_LENGTH+1):
            flash(f'Email must be between {MINIMUM_EMAIL_LENGTH} and {MAX_FORM_LENGTH} characters', category='error')

        #No. 4: Passwords must contain at least 8 characters
        elif len(pw1) not in range(MINIMUM_PASSWORD_LENGTH,MAXIMUM_PASSWORD_LENGTH+1):
            flash(f'Password must be between {MINIMUM_PASSWORD_LENGTH} and {MAXIMUM_PASSWORD_LENGTH} characters', category='error')
          
        #No. 3: Passwords must match    
        elif pw1 != pw2:
            flash('Passwords do not match', category='error')
        else:
          user_data = {
            "email":email,
            "full_name":full_name,
            "password":generate_password_hash(pw1,"sha256")
          }
          db[email] = user_data
          

    else:
      user_ip = request.environ.get("HTTP_X_FORWARDED_FOR")
      closest_schools = get_closest_schools(user_ip)
      tags = get_tags()
      return render_template("sign-up.html", user=current_user,closest_schools=closest_schools,tags=tags)
      
#settings page
@auth.route('/settings', methods=['GET', 'POST'])
#@login_required
def settings():
  print(db.keys())
  if request.method=='POST':
   
    if request.form['submit'] == 'e':
      email = request.form.get('email')

      if len(email) not in range(MINIMUM_EMAIL_LENGTH, MAX_FORM_LENGTH+1):
        flash('Email cannot be empty', category='error')

      else:
        print("valid")
        
        
    if request.form['submit'] == 'p':
      pw1 = request.form.get('password1')
      pw2 = request.form.get('password2')

      if len(pw1) not in range(MINIMUM_PASSWORD_LENGTH,MAXIMUM_PASSWORD_LENGTH+1):
        flash('INVALID PASSWORD', category='error')

      elif pw1 != pw2:
        flash('PASSWORDS DONT MATCH', category='error')

      else:
        print("valid")
        
    if request.form['submit'] == 'n':
      name = request.form.get('name')

      if len(name) not in range(MINIMUM_FULL_NAME_LENGTH, MAX_FORM_LENGTH+1):
            flash(f'Name must be between {MINIMUM_FULL_NAME_LENGTH} and {MAX_FORM_LENGTH} characters', category='error')

      else:
        print("valid")
      
  else:
    return render_template("settings.html", user=current_user)
  