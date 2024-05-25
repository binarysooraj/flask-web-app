import certifi
from pymongo import MongoClient
import ssl

print(ssl.OPENSSL_VERSION)  # Print OpenSSL version for verification

uri = 'mongodb+srv://soorajbinary:1rkptm6BRGpFMTVs@cluster0.povmgmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    
try:
    client = MongoClient(uri, tlsCAFile=certifi.where())

    # Test the connection
    client.admin.command('ping')
    print("Connection successful")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Server selection timeout error: {err}")
except pymongo.errors.ConnectionFailure as err:
    print(f"Connection failure: {err}")
except Error as err:
    print(f"Configuration error: {err}")
except Exception as err:
    print(f"An unexpected error occurred: {err}")
