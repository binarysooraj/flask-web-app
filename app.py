from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message
import cloudinary
import cloudinary.uploader
import cloudinary.api
import certifi
from predict import forecast
from datetime import date
import json
import json
import plotly.graph_objs as go
import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to your preferred secret key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'  # Change this to your preferred secret key

# MongoDB connection
client = MongoClient(
    'mongodb+srv://soorajbinary:1rkptm6BRGpFMTVs@cluster0.povmgmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
    tlsCAFile=certifi.where()
)


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

def getStocksData():
    # Open and read the JSON file correctly
    with open('51_stocks_data.json', 'r') as file:
        data = json.load(file)  # Use json.load to read from a file
    
    # Extract the latest date data
    result = []

    for stock, dates in data.items():
        latest_date = max(dates.keys())
        print('latest_date: ', latest_date)
        latest_data = dates[latest_date]
        print('latest_data: ', latest_data)
        latest_data["name"] = stock
        result.append(latest_data)

    # Output the result
    return jsonify(stocks=result)

def load_stock_data():
    with open('model_files/51_stocks_data.json') as f:
        return json.load(f)

def create_plot():
    stock_data = load_stock_data()
    
    fig = go.Figure()
    
    for symbol, data in stock_data.items():
        print(symbol)
        print(data)
        dates = []
        prices = []
        for date, values in data.items():
            dates.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
            prices.append(float(values['4. close']))
        
        hover_text = [f"{symbol}: {date.strftime('%Y-%m-%d')}" for date in dates]
        
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=symbol, hovertext=hover_text))

    fig.update_layout(
        title='Closing Prices of Stocks',
        xaxis_title='Date',
        yaxis_title='Close Price (USD)',
        hovermode='closest',
        xaxis=dict(
            tickformat='%b %Y'
        )
    )
    
    return fig


# Routes
@app.route('/')
def index():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            plot = create_plot()
            return render_template('index.html', plot=plot.to_html(full_html=False, include_plotlyjs='cdn'), user=user)
    else:
            return redirect(url_for('signin'))
    




@app.route('/purchaseStocks')
def purchaseStocks():
    if 'user' in session:
        user = session['user']
            # Open and read the JSON file correctly
        with open('model_files/51_stocks_data.json', 'r') as file:
            data = json.load(file)  # Use json.load to read from a file
        
        # Extract the latest date data
        result = []

        for stock, dates in data.items():
            latest_date = max(dates.keys())
            print('latest_date: ', latest_date)
            latest_data = dates[latest_date]
            latest_data["name"] = stock
            latest_data["latest_date"] = latest_date
            result.append(latest_data)

        # Output the result
        # return jsonify(stocks=result)
        return render_template('tables-data.html', user=user, stocks=result)
    else:
        return redirect(url_for('signin'))
    

@app.route('/stocks_data')
def getStocksData():
    if 'user' in session:
        user = session['user']
            # Open and read the JSON file correctly
        with open('model_files/51_stocks_data.json', 'r') as file:
            data = json.load(file)  # Use json.load to read from a file
        
        # Extract the latest date data
        result = []

        for stock, dates in data.items():
            latest_date = max(dates.keys())
            print('latest_date: ', latest_date)
            latest_data = dates[latest_date]
            latest_data["name"] = stock
            latest_data["latest_date"] = latest_date
            result.append(latest_data)

        # Output the result
        # return jsonify(stocks=result)
        return render_template('tables-general.html', user=user, stocks=result)
    else:
        return redirect(url_for('signin'))


    

@app.route('/predict')
def predict():
    today = date.today()
    print("Today's date:", today)
    predictions = forecast(today)
    predictions =  predictions.tolist()
    print('predictions: ', predictions[0])
    return jsonify(predictions=predictions)


@app.route('/calculate_risk')
def calculate_risk():

    today = date.today()
    print("Today's date:", today)
    current_prices = forecast(today)
    current_prices =  current_prices.tolist()[0]
    print('current_prices: ', current_prices[0])
    # current_price=12
    # purchase_price = 10

    purchase_prices = [165.0, 144.5699920654297, 131.40000915527344, 344.47003173828125, 367.75, 475.6900634765625, 142.0500030517578, 468.5000305175781, 29.85000228881836, 135.32000732421875, 462.83001708984375, 56.130001068115234, 46.790000915527344, 102.45999908447266, 159.1599884033203, 251.12001037597656, 148.52000427246094, 57.57999801635742, 62.56999588012695, 132.55999755859375, 68.04999542236328, 257.9800109863281, 418.7699890136719, 89.29000091552734, 31.73000144958496, 46.439998626708984, 167.08999633789062, 51.11000061035156, 376.9100036621094, 83.9000015258789, 16.09000015258789, 37.30999755859375, 156.8300018310547, 37.869998931884766, 96.80000305175781, 141.8199920654297, 106.93000030517578, 25.260000228881836, 107.6300048828125, 144.4499969482422, 439.20001220703125, 145.72999572753906, 58.060001373291016, 162.0399932861328, 265.42999267578125, 58.6099967956543, 331.969970703125, 644.6900024414062, 137.39999389648438, 88.83999633789062, 72.5]
    print('purchase_prices: ', purchase_prices)

    risk_list = []
    
    for i in range(0, len(purchase_prices)):

        print('\n\n')
        print('Current price: ', current_prices[i])
        print('Purchase_proce:', purchase_prices[i])

        risk = current_prices[i] - (purchase_prices[i])

        risk_list.append(risk)

    return jsonify(risk_list=risk_list)


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
            'image_url': '',
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
    

@app.route('/profile')
def profile():
    # Check if user is logged in
        if 'user' in session:
            user = session['user']        
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
        image_url = ''
        file = request.files['file']
        if file:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result.get('url')
        user = session['user']
        updated_fields = {  
            'image_url': image_url,
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


# Configure Cloudinary credentials
cloudinary.config(
    cloud_name='daxa9xef8',
    api_key='553891686579191',
    api_secret='cmfGWd0Nkvw0rdGIA5JXPLW1ps0'
)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


