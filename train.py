import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import joblib


# Constants
TIME_STEP = 60

def load_stock_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_close_prices(stock_data):
    close_prices = pd.DataFrame(index=pd.to_datetime([]))
    for symbol, data in stock_data.items():
        prices = [float(data[date]["4. close"]) for date in data]
        dates = list(data.keys())
        symbol_df = pd.DataFrame(prices, index=pd.to_datetime(dates), columns=[symbol])
        close_prices = pd.concat([close_prices, symbol_df], axis=1)
    return close_prices

def create_lstm_dataset(data, time_step):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:(i + time_step)])
        y.append(data[i + time_step])
    return np.array(X), np.array(y)

# Load data from JSON file
file_path = 'model_files/51_stocks_data.json'  # Replace with your JSON file path
all_stock_data = load_stock_data_from_json(file_path)

# Extract close prices
close_prices_df = extract_close_prices(all_stock_data)
close_prices_df.to_csv('model_files/51_stock_data.csv', index=True)

# Handle any missing values by forward filling and then back filling
close_prices_df = close_prices_df.fillna(method='ffill').fillna(method='bfill')

# Check if any NaN values remain
if close_prices_df.isnull().values.any():
    print("There are still missing values in the DataFrame.")
else:
    print("All missing values have been handled.")

# Normalize the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_prices_df)
joblib.dump(scaler, 'model_files/scaler.pkl')

# Prepare data for LSTM
X, y = create_lstm_dataset(scaled_data, TIME_STEP)
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Define and train the LSTM model
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(units=50, return_sequences=False),
    Dense(units=25),
    Dense(units=close_prices_df.shape[1])  # Output layer with number of stocks as nodes
])

model.summary()

# Save the entire model
model.save('model_files/lstm_model.h5')

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

# Train the model and capture the training history
history = model.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test))

# Evaluate the model on the test set
test_loss = model.evaluate(X_test, y_test)
print(f"Test Loss: {test_loss}")

# Plot training and validation loss
plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
