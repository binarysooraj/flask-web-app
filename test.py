# import certifi
# from pymongo import MongoClient
# import ssl

# print(ssl.OPENSSL_VERSION)  # Print OpenSSL version for verification

# uri = 'mongodb+srv://soorajbinary:1rkptm6BRGpFMTVs@cluster0.povmgmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    
# try:
#     client = MongoClient(uri, tlsCAFile=certifi.where())

#     # Test the connection
#     client.admin.command('ping')
#     print("Connection successful")
# except pymongo.errors.ServerSelectionTimeoutError as err:
#     print(f"Server selection timeout error: {err}")
# except pymongo.errors.ConnectionFailure as err:
#     print(f"Connection failure: {err}")
# except Error as err:
#     print(f"Configuration error: {err}")
# except Exception as err:
#     print(f"An unexpected error occurred: {err}")

import json

def getStocksData():
    # Open and read the JSON file correctly
    with open('model_files/51_stocks_data.json', 'r') as file:
        data = json.load(file)  # Use json.load to read from a file

    last_date = sorted(data.keys(), reverse=True)[0]
    last_date_values = data[last_date]

    stocks = []

    # Prepare the stocks data
    for key, value in last_date_values.items():
        stocks.append({"key": key, "value": value})

    return stocks
            

print(getStocksData())      