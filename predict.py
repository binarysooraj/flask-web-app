# forecast.py
import pickle
import pandas as pd
import numpy as np

MODELS_SAVE_PATH = 'model_files/garch_models.pkl'

def load_models(file_path):
    with open(file_path, 'rb') as file:
        models = pickle.load(file)
    return models

def extract_close_prices(stock_data):
    close_prices = pd.DataFrame(index=pd.to_datetime([]))
    for symbol, data in stock_data.items():
        prices = [float(data[date]["4. close"]) for date in data]
        dates = list(data.keys())
        symbol_df = pd.DataFrame(prices, index=pd.to_datetime(dates), columns=[symbol])
        close_prices = pd.concat([close_prices, symbol_df], axis=1)
    return close_prices

def forecast_price_for_specific_date(symbol, model_fit, last_price, forecast_horizon):
    forecast = model_fit.forecast(horizon=forecast_horizon)
    predicted_volatility = forecast.variance[-1:].values.flatten()
    predicted_returns = np.random.normal(0, np.sqrt(predicted_volatility), forecast_horizon)
    predicted_price = last_price * (1 + predicted_returns / 100).cumprod()
    return predicted_price

def predict_specific_date(stock_data, specific_date, models_path=MODELS_SAVE_PATH):
    models = load_models(models_path)
    close_prices_df = extract_close_prices(stock_data)

    specific_date_timestamp = pd.Timestamp(specific_date)
    days_to_specific_date = (specific_date_timestamp - close_prices_df.index[-1]).days

    if days_to_specific_date > 0:
        specific_date_predicted_prices = {}

        for symbol in close_prices_df.columns:
            if symbol in models:
                last_price = close_prices_df[symbol].iloc[-1]
                forecast_horizon = days_to_specific_date
                predicted_prices_for_symbol = forecast_price_for_specific_date(
                    symbol, models[symbol], last_price, forecast_horizon)
                specific_date_predicted_prices[symbol] = predicted_prices_for_symbol[-1]

        return specific_date_predicted_prices
    else:
        raise ValueError(f"Cannot predict for {specific_date} as it is in the past or too close to the last date in the dataset.")
