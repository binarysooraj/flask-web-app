import joblib
from keras.models import load_model
import pandas as pd
import pickle
import numpy as np

# Constants
TIME_STEP = 60

# Predict for a specific date
def forecast(specific_date):
  specific_date_timestamp = pd.Timestamp(specific_date)

  close_prices_df = pd.read_csv('model_files/51_stock_data.csv')
  close_prices_df.index = pd.to_datetime(close_prices_df.iloc[:, 0], errors='coerce')
  close_prices_df = close_prices_df.iloc[:, 1:]

  scaler = joblib.load('model_files/scaler.pkl')
  scaled_data = scaler.transform(close_prices_df)

  # Load the model
  model = load_model('model_files/lstm_model.h5')

  steps_ahead = (specific_date_timestamp - close_prices_df.index[-1]).days  # Number of days ahead

  if steps_ahead < 0:
      print(f"The specific date {specific_date} is in the past relative to the last available date in the dataset.")
  else:
      input_data = scaled_data[-TIME_STEP:]
      for step in range(steps_ahead):
          input_data_reshaped = input_data.reshape(1, TIME_STEP, -1)
          predicted_scaled = model.predict(input_data_reshaped)
          predicted_price = scaler.inverse_transform(predicted_scaled)

          # Append the predicted data to input_data for the next prediction
          next_input = predicted_scaled[0]
          input_data = np.vstack([input_data[1:], next_input])

      # The final predicted price after iterating through steps_ahead
      print(f"Predicted Price for {specific_date}: {predicted_price[0]}")
      return predicted_price

# result = forecast("2024-05-17")
# print(result)