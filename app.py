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
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to your preferred secret key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'  # Change this to your preferred secret key

# MongoDB connection
client = MongoClient(
    'mongodb+srv://stockpricepredictionfyp:7rZ18BFVmJ129ysl@cluster0.zswnrqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
    tlsCAFile=certifi.where()
)
db = client['demo']
users_collection = db['users']
posts_collection = db['posts']
stocks_collection = db['stocks']
stocks_history_collection = db['stock_history']

posts = []

app.config['MAIL_SERVER']= 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = 'bade8f2c6fea75faf8fe2a32846718bb'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


# Configure Cloudinary credentials
cloudinary.config(
    cloud_name='daxa9xef8',
    api_key='553891686579191',
    api_secret='cmfGWd0Nkvw0rdGIA5JXPLW1ps0'
)



def getStocksData():
    # Open and read the JSON file correctly
    with open('model_files/51_stocks_data.json', 'r') as file:
        data = json.load(file)  # Use json.load to read from a file
    
    # Extract the latest date data
    result = []

    for stock, dates in data.items():
        latest_date = max(dates.keys())
        latest_data = dates[latest_date]
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
        dates = []
        prices = []
        for date, values in data.items():
            dates.append(datetime.strptime(date, '%Y-%m-%d'))
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
            print(user)
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            plot = create_plot()
            return render_template('index.html', plot=plot.to_html(full_html=False, include_plotlyjs='cdn'), user=user)
    else:
            return redirect(url_for('signin'))
    



@app.route('/purchase', methods=['POST'])
def purchase_stock():
    if 'user' not in session:
        return jsonify({"message": "User not logged in"}), 401

    data = request.get_json()
    stock_index = data.get('stockIndex')
    stock_price = data.get('stockPrice')
    stock_name = data.get('stockName')
    number_of_stocks = data.get('numberOfStocks')
    total_charges = data.get('totalCharges')

    user = users_collection.find_one({'uid': session['user']['uid']})
   
    if user['wallet'] < total_charges:
        return jsonify({"message": "Insufficient funds in your wallet"}), 400

    # Deduct the total charges from the user's wallet
    new_wallet_balance = user['wallet'] - total_charges
    new_total_purchase = user['total_purchase'] + total_charges
    users_collection.update_one({'uid': session['user']['uid']}, {'$set': {'wallet': new_wallet_balance, 'total_purchase': new_total_purchase}})
    
    
    date_of_purchase = datetime.now().strftime('%Y-%m-%d')


    # Store the purchase details in the stocks collection
    stock_purchase = {
        'uid': session['user']['uid'],
        'stock_index': stock_index,
        'stock_name': stock_name,
        'price': stock_price,
        'date_of_purchase': date_of_purchase,
        'volume': number_of_stocks,
        'totalCharges': total_charges,
        'type':'purchase'
    }
    stocks_collection.insert_one(stock_purchase)
    stocks_history_collection.insert_one(stock_purchase)
    
    user = session['user']
    updated_fields = {  
        'wallet': new_wallet_balance,
        'total_purchase': new_total_purchase
    }

    # Update user details in the session
    for key, value in updated_fields.items():
        user[key] = value
    session['user'] = user

    return jsonify({"message": "Stocks purchased successfully"})

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
        
        # Fetch stocks data for the logged-in user
        user_stocks = stocks_collection.find({'uid': user['uid']})
        
        # Prepare result list to store filtered stocks data
        result = []

        for stock in user_stocks:
            stock['_id'] = str(stock['_id'])  # Convert ObjectId to string
            result.append(stock)

        # Output the result
        return render_template('tables-general.html', user=user, stocks=result)
    else:
        return redirect(url_for('signin'))



    

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    stock_index = data.get('stockIndex')
    date = data.get('date')
    
    # Ensure the date is in the correct format and valid
    try:
        forecast_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    # Call your forecasting function with the provided date
    predictions = forecast(date)
    
    # Ensure the predictions are in a list format
    predictions = predictions.tolist() if hasattr(predictions, 'tolist') else predictions
    
    return jsonify(predictions=predictions)


@app.route('/calculate_risk', methods=['POST'])
def calculate_risk():
    data = request.get_json()
    index = data.get('index')
    date = data.get('date')
    purchase_price = data.get('purchasePrice')

    # Assuming you have a function forecast that retrieves current prices
    current_prices = forecast(date)
    current_price = current_prices[0][index]
    
    try:
        # Convert purchase_price to float if it's not already
        purchase_price = float(purchase_price)

        # Convert current_price to float if it's not already
        current_price = float(current_price)

        # Calculate risk
        risk = current_price - purchase_price
        return jsonify(risk=risk)
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/history')
def history():
    if 'user' in session:
            user = session['user']
            # Fetch user's posts from the database
            # user_posts = posts_collection.find({'user_id': user['_id']})
            # Fetch stocks data for the logged-in user
            user_stocks = stocks_history_collection.find({'uid': user['uid']})
            
            # Prepare result list to store filtered stocks data
            result = []

            for stock in user_stocks:
                stock['_id'] = str(stock['_id'])  # Convert ObjectId to string
                result.append(stock)
            return render_template('history-data.html', user=user, stocks=result)
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
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists  
        if users_collection.find_one({'email': email}):
            error = "User already exists"
        else:
            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Generate unique uid
            uid = str(uuid.uuid4())

            # Insert user into database
            users_collection.insert_one({
                'uid': uid,
                'image_url': '.............',
                'username': username,
                'email': email,
                'contact': '.............',
                'address': '.............',
                'password': hashed_password,
                'city': '.............',
                'country': '.............',
                'wallet': 50000,
                'total_purchase':0,
                'total_sold':0
            })
            return redirect(url_for('signin'))

    return render_template('pages-register.html', error=error)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
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
                'image_url': user['image_url'],
                'total_sold': user['total_sold'],
                'total_purchase': user['total_purchase'],
                'username': user['username'],
                'email': user['email'],
                'contact': user['contact'],
                'address': user['address'],
                'city': user['city'],
                'country': user['country'],
                'wallet': user['wallet'],
                'linkedin': user['linkedin'],
                'twitter': user['twitter'],
                'instagram': user['instagram'],
                'facebook': user['facebook'],
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
        return redirect(url_for('index'))
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
    if 'user' not in session:
        return jsonify({"message": "You need to log in to change your password"}), 401

    user = session['user']
    current_password = request.json['currentPassword']
    new_password = request.json['newPassword']
    renew_password = request.json['renewPassword']

    # Fetch user from the database
    db_user = users_collection.find_one({'uid': user['uid']})

    # Check if current password is correct
    if not bcrypt.check_password_hash(db_user['password'], current_password):
        return jsonify({"message": "Current password is incorrect"}), 401

    # Check if new passwords match
    if new_password != renew_password:
        return jsonify({"message": "New passwords do not match"}), 400

    # Hash new password
    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update user's password in the database
    users_collection.update_one(
        {'uid': user['uid']},
        {'$set': {'password': hashed_new_password}}
    )

    return jsonify({"message": "Password successfully changed"}), 200




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



@app.route('/sell', methods=['POST'])
def sell_stock():
    if 'user' not in session:
        return jsonify({"message": "User not logged in"}), 401

    data = request.get_json()
    stock_index = data.get('stockIndex')
    stock_price = data.get('stockPrice')
    id = data.get('id')
    number_of_stocks = data.get('numberOfStocks')

    user = users_collection.find_one({'uid': session['user']['uid']})

    # Check if the user has the stock in their possession
    user_stock = stocks_collection.find_one({'_id': ObjectId(id)})
    if not user_stock:
        return jsonify({"message": "User does not possess this stock"}), 400

    # Check if the user has enough stocks to sell
    if int(user_stock['volume']) < int(number_of_stocks):
        return jsonify({"message": "User does not have enough stocks to sell"}), 400

    # Calculate the total charges for the sale
  
    total_charges = float(stock_price) * int(number_of_stocks)

    # Update the user's wallet balance
    new_wallet_balance = user['wallet'] + total_charges
    new_total_sold = user['total_sold'] + total_charges

    users_collection.update_one({'uid': session['user']['uid']}, {'$set': {'wallet': new_wallet_balance, 'total_sold': new_total_sold}})
    # Update the volume of the sold stock in the stocks collection
    new_volume = int(user_stock['volume']) - int(number_of_stocks)
    user_stock['type'] = "sell"
    stocks_history_collection.insert_one(user_stock)

    if new_volume > 0:
            stocks_collection.update_one(
                {'uid': session['user']['uid'], 'stock_index': stock_index},
                {'$set': {'volume': new_volume}}
            )
    else:
            stocks_collection.delete_one({'uid': session['user']['uid'], 'stock_index': stock_index})
    
    user = session['user']
    updated_fields = {  
        'wallet': new_wallet_balance,
        'total_sold': new_total_sold
    }

    # Update user details in the session
    for key, value in updated_fields.items():
        user[key] = value
    session['user'] = user

    return jsonify({"message": "Stocks sold successfully"}), 200



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")



