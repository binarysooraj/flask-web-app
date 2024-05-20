from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message



app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to your preferred secret key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'  # Change this to your preferred secret key

# MongoDB connection
client = MongoClient('mongodb+srv://soorajbinary:1rkptm6BRGpFMTVs@cluster0.povmgmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['demo']
users_collection = db['users']
posts_collection = db['posts']

app.config['MAIL_SERVER']= 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = 'bade8f2c6fea75faf8fe2a32846718bb'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Routes
@app.route('/')
def index():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('index.html', user=user)
    else:
            return redirect(url_for('signin'))
    

@app.route('/purchaseStocks')
def purchaseStocks():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('tables-data.html', user=user)
    else:
            return redirect(url_for('signin'))
    


@app.route('/sellStocks')
def sellStocks():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('tables-general.html', user=user)
    else:
            return redirect(url_for('signin'))
    

@app.route('/history')
def history():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('history-data.html', user=user)
    else:
            return redirect(url_for('signin'))
    

@app.route('/contact')
def contact():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('pages-contact.html', user=user)
    else:
            return redirect(url_for('signin'))
    
    

@app.route('/learn')
def learn():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('learn.html', user=user)
    else:
            return redirect(url_for('signin'))
    


@app.route('/components-modal')
def componentsModal():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('components-modal.html', user=user)
    else:
            return redirect(url_for('signin'))
    


@app.route('/components-pagination')
def componentsPagination():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('components-pagination.html', user=user)
    else:
            return redirect(url_for('signin'))
    return render_template('components-pagination.html')


@app.route('/components-progress')
def componentProgress():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('components-progress.html', user=user)
    else:
            return redirect(url_for('signin'))
    return render_template('components-progress.html')


@app.route('/components-spinners')
def componentSpinners():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('components-spinners.html', user=user)
    else:
            return redirect(url_for('signin'))
    return render_template('components-spinners.html')

posts = []



# Endpoint to handle form submission
@app.route('/create-post', methods=['POST'])
def create_post():
    # Get data from the form
    post_title = request.form['postTitle']
    post_content = request.form['postContent']
    
    # Create a new post document
    post = {
        'title': post_title,
        'content': post_content
    }
    
    # Insert the post document into the MongoDB collection
    result = posts_collection.insert_one(post)
    
    # Check if insertion was successful
    if result.inserted_id:
        return 'OK'
    else:
        return 'error Failed to create post' # HTTP status code 500: Internal Server Error


@app.route('/pages-contact')
def contactPage():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('pages-contact.html', user=user)
    else:
            return redirect(url_for('signin'))


@app.route('/pages-about')
def aboutPage():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('about-page.html', user=user)
    else:
            return redirect(url_for('signin'))




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        profile_picture = 'profile'
        # profile_picture = request.form['profile_picture']
        username = request.form['username']
        email = request.form['email']
        # contact = request.form['contact']
        # address = request.form['address']
        password = request.form['password']
        # city = request.form['city']
        # country = request.form['country']
        city = 'city'
        country = 'country'
        address = 'address'
        contact = '91313123322'

        # Simple form validation
        if not (profile_picture and username and email and contact and address and password and city and country):
            return "All fields are required", 400

        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return "User already exists", 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Generate unique uid
        uid = str(uuid.uuid4())

        # Insert user into database
        users_collection.insert_one({
            'uid': uid,
            'profile_picture': profile_picture,
            'username': username,
            'email': email,
            'contact': contact,
            'address': address,
            'password': hashed_password,
            'city': city,
            'country': country,
            'wallet': 500
        })

        return redirect(url_for('signin'))

    return render_template('pages-register.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            # Generate JWT token
            access_token = create_access_token(identity=str(user['_id']))
            # Store user details and token in session
            session['user'] = {
                'uid': user['uid'],
                'profile_picture': user['profile_picture'],
                'username': user['username'],
                'email': user['email'],
                'contact': user['contact'],
                'address': user['address'],
                'city': user['city'],
                'country': user['country'],
                'wallet': user['wallet'],
                'access_token': access_token
            }
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password", 401

    return render_template('pages-login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if user is logged in
    if 'user' in session:
        user = session['user']
        if request.method == 'POST':
            # Create post logic
            pass
        return render_template('index.html', user=user)
    else:
        return redirect(url_for('signin'))
    
    
# @app.route('/update_profile', methods=['POST'])
# def update_profile():
    if 'user' in session:
        user = session['user']
        updated_user = {
            'uid': user['uid'],
            'profile_picture': request.form['profile_picture'],
            'username': request.form['username'],
            'contact': request.form['contact'],
            'address': request.form['address'],
            'city': request.form['city'],
            'country': request.form['country']
        }
        # Update user in the database
        users_collection.update_one({'uid': user['uid']}, {'$set': updated_user})
        # Update user in session
        session['user'].update(updated_user)
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('signin'))

@app.route('/profile')
def profile():
    # Check if user is logged in
        if 'user' in session:
            user = session['user']
            print("Inside if: "+user['country'])
        
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            return render_template('users-profile.html', user=user)
        else:
            return redirect(url_for('signin'))

@app.route('/signout')
def signout():
    # Clear the user session
    session.pop('user', None)
    return redirect(url_for('index'))  # Redirect to the index or login page



@app.route('/change-password', methods=['POST'])
def change_password():
    if 'user' in session:
        user = session['user']
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        renew_password = request.form['renewPassword']

        # Fetch user from the database
        db_user = users_collection.find_one({'uid': user['uid']})

        # Check if current password is correct
        if not bcrypt.check_password_hash(db_user['password'], current_password):
            return "Current password is incorrect", 401

        # Check if new passwords match
        if new_password != renew_password:
            return "New passwords do not match", 400

        # Hash new password
        hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # Update user's password in the database
        users_collection.update_one(
            {'uid': user['uid']},
            {'$set': {'password': hashed_new_password}}
        )

        return redirect(url_for('profile'))

    else:
        return redirect(url_for('signin'))
    
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' in session:
        user = session['user']
        updated_fields = {
            'about': request.form['about'],
            'city': request.form['city'],
            'country': request.form['country'],
            'address': request.form['address'],
            'contact': request.form['phone'],
            'email': request.form['email'],
            'twitter': request.form['twitter'],
            'facebook': request.form['facebook'],
            'instagram': request.form['instagram'],
            'linkedin': request.form['linkedin']
        }

        # Update user in the database
        users_collection.update_one({'uid': user['uid']}, {'$set': updated_fields})

        # Update user details in the session
        for key, value in updated_fields.items():
            user[key] = value
        session['user'] = user

        return redirect(url_for('profile'))
    else:
        return redirect(url_for('signin'))






@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Set up SMTP connection
        smtp_server = 'live.smtp.mailtrap.io'
        smtp_port = 587  # Change to the appropriate port for your SMTP server
        sender_email = 'soorajbinary@demomailtrap.com'
        sender_password = 'bade8f2c6fea75faf8fe2a32846718bb'
        recipients = [email]
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject

        # Creating the message
        msg = Message(name,
                        sender="soorajbinary@demomailtrap.com",
                        recipients=recipients)
        msg.body = message

        # Sending the email
        mail.send(msg)

        return "OK"

# Endpoint to fetch all posts
@app.route('/pages-faq', methods=['GET'])
def get_posts():
    # Retrieve all posts from the MongoDB collection
    posts = list(posts_collection.find({}, {'_id': 0}))  # Exclude _id field from the response
    
    if 'user' in session:
            user = session['user']
            # Check if there are any posts
            if posts:
                return render_template('pages-faq.html', user=user, posts=posts)
            else:
                return render_template('pages-faq.html', user=user, posts=[])
    else:
            return redirect(url_for('signin'))        

# Function to handle uploading of profile image
@app.route('/upload-profile-image', methods=['POST'])
def upload_profile_image():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'Profile image uploaded successfully'
    else:
        return 'Failed to upload profile image'

# Function to handle removal of profile image
@app.route('/remove-profile-image')
def remove_profile_image():
    # Add your logic here to remove the profile image
    # For example, you can delete the file from the filesystem
    return 'Profile image removed successfully'

if __name__ == '__main__':
    app.run(debug=True)
