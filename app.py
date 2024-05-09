from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient 

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MongoDB setup
client = MongoClient('mongodb+srv://soorajbinary:1rkptm6BRGpFMTVs@cluster0.povmgmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['demo']
users_collection = db['users']

# Existing routes
@app.route('/') 
def hello_world(): 
    return 'Hello, World!'

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_collection.find_one({'username': username}):
            return 'Username already exists!'
        users_collection.insert_one({'username': username, 'password': password})
        session['username'] = username  # Set the 'username' in session upon successful login
        return redirect(url_for('dashboard'))  # Redirect to dashboard after signup
    return render_template('signup.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username  # Set the 'username' in session upon successful login
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            return 'Invalid username or password!'
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Render dashboard template
    return render_template('dashboard.html')

# User profile route
@app.route('/profile')
def profile():
    if 'username' in session:
        # Get user details from the database based on the logged-in user
        user_details = users_collection.find_one({'username': session['username']})
        if user_details:
            # Render user profile template with user details
            return render_template('profile.html', user=user_details)
        else:
            return 'User not found!'
    else:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

if __name__ == '__main__': 
    app.run()