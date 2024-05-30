# train.py
import json
import pandas as pd
import numpy as np
from arch import arch_model
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Constants
JSON_FILE_PATH = 'model_files/51_stocks_data.json'
MODELS_SAVE_PATH = 'model_files/garch_models.pkl'

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

def split_data(close_prices, test_size=0.2):
    train_size = int(len(close_prices) * (1 - test_size))
    train_data, test_data = close_prices[:train_size], close_prices[train_size:]
    return train_data, test_data

def garch_forecast(symbol, returns, last_price, forecast_horizon):
    model = arch_model(returns, vol='Garch', p=1, q=1)
    model_fit = model.fit(disp="off")
    forecast = model_fit.forecast(horizon=forecast_horizon)
    predicted_volatility = forecast.variance[-1:].values.flatten()
    predicted_returns = np.random.normal(0, np.sqrt(predicted_volatility), forecast_horizon)
    predicted_price = last_price * (1 + predicted_returns / 100).cumprod()
    return model_fit, predicted_price

def train_models():
    all_stock_data = load_stock_data_from_json(JSON_FILE_PATH)
    SYMBOLS = all_stock_data.keys()
    close_prices_df = extract_close_prices(all_stock_data)

    trained_models = {}
    performance_metrics = {}

    for symbol in SYMBOLS:
        if symbol in close_prices_df:
            train_data, test_data = split_data(close_prices_df[symbol])
            returns_train = train_data.pct_change().dropna() * 100  # Calculate returns and convert to percentage
            returns_test = test_data.pct_change().dropna() * 100
            last_price_train = train_data.iloc[-1]

            model_fit, predicted_prices_train = garch_forecast(symbol, returns_train, last_price_train, len(test_data))
            trained_models[symbol] = model_fit

            # Align the lengths of actual and predicted test prices
            actual_prices_test = test_data.values[1:]  # Skip the first value due to differencing in returns
            if len(predicted_prices_train) > len(actual_prices_test):
                predicted_prices_train = predicted_prices_train[:len(actual_prices_test)]
            elif len(predicted_prices_train) < len(actual_prices_test):
                actual_prices_test = actual_prices_test[:len(predicted_prices_train)]

            # Calculate metrics on test data
            mse = mean_squared_error(actual_prices_test, predicted_prices_train)
            mae = mean_absolute_error(actual_prices_test, predicted_prices_train)
            performance_metrics[symbol] = {'MSE': mse, 'MAE': mae}

    # Save the trained models to a file
    with open(MODELS_SAVE_PATH, 'wb') as file:
        pickle.dump(trained_models, file)

    return performance_metrics

if __name__ == "__main__":
    performance_metrics = train_models()
    print("Model Performance Metrics:")
    for symbol, metrics in performance_metrics.items():
        print(f"{symbol}: MSE = {metrics['MSE']}, MAE = {metrics['MAE']}")
