import sqlite3

from flask import Flask
from markupsafe import escape
from flask import url_for
from flask import request,jsonify
from flask import render_template
from flask import session

from setupDB import add_new_user
from setupDB import get_user

#f'{}' f is a format to string literal

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this_later'


@app.route("/")
def homepage():
	return render_template("index.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        return do_the_register()
    else:
        return show_the_register_form()

def show_the_register_form():
    return render_template("auth/register.html")

def do_the_register():
    #unpacks json data sent from js
    data = request.get_json()

    #extracts specific variables 
    uName = data.get('username')
    passW = data.get('password')

    is_successful = add_new_user(uName, passW)

    if(is_successful == True):
        return jsonify({"status": "successful", "message": f"Registration received for {uName}.. redirecting to login page"})
    elif (is_successful == False):
        return jsonify({"status": "unsuccessful", "message": f"Registration was not received for {uName} due to an error, the username is already taken"})
    #sends result data to the browser through JSON
  

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()

def show_the_login_form():
	return render_template("auth/login.html")

def do_the_login():
    data = request.get_json()

    uName = data.get('username')
    passW = data.get('password')

    user_row = get_user(uName) # Pass the username here!

    #if the returned tuple is empty
    if (user_row is None):
        return jsonify({"status": "unsuccessful", "message": "Login unsuccessful, username not found"})
    
    #If they exist, check the password (stored at index 2)
    db_password = user_row[2]

    if (db_password == passW):
        #saves the name in the cookie
        session['logged_in_user'] = uName
        return jsonify({"status": "successful", "message": "Login successful"})
    else:
        return jsonify({"status": "unsuccessful", "message": "Login unsuccessful, password not correct"})

@app.route("/user/<username>")
def profile(username):
    #check if the cookie exists and matches the URL
    if 'logged_in_user' not in session or session['logged_in_user'] != username:
        return "Access Denied: you must be logged in as a user to view this page"

    user_data = get_user(username)
    return f"<h1>Welcome to your profile, {user_data[1]}!</h1>"

with app.test_request_context():
	print(url_for('homepage'))

	print(url_for('login'))
	print(url_for('login', next = '/'))

	url_for('static', filename='style.css')


if __name__ == "__main__":
    app.run(debug=False)