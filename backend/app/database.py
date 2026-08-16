from pymongo import MongoClient
# MongoDB ke sath connection banane ke liye MongoClient import kar rahe hain


from dotenv import load_dotenv
# .env file se hidden variables (jaise database URL) load karne ke liye


import os
# Operating system ke environment variables access karne ke liye




# Load .env file
load_dotenv()
# Ye .env file ko read karta hai
# Example:
# .env ke andar:
# MONGO_URL=mongodb://localhost:27017
# DATABASE_NAME=smart_surveillance
#
# Ye values memory me load ho jati hain




# Read environment variables
MONGO_URL = os.getenv("MONGO_URL")
# .env file se MongoDB ka URL nikal raha hai
#
# Example:
# MONGO_URL = "mongodb://localhost:27017"




DATABASE_NAME = os.getenv("DATABASE_NAME")
# .env file se database ka naam nikal raha hai
#
# Example:
# DATABASE_NAME = "smart_surveillance"






# Create MongoDB client
client = MongoClient(MONGO_URL)
# MongoDB server ke sath connection bana raha hai
#
# Matlab:
# Python application  <---->  MongoDB Server
#
# Ab Python MongoDB se data send aur receive kar sakta hai






# Select database
db = client[DATABASE_NAME]
# MongoDB ke andar jis database ka naam .env me diya hai
# us database ko select kar raha hai
#
# Example:
# MongoDB
#    |
#    |--- smart_surveillance
#
# Ye wahi database open karega






# Collections
users_collection = db["users"]
# Database ke andar users naam ka collection select kar raha hai
#
# Structure:
#
# smart_surveillance (Database)
#          |
#          |
#       users (Collection)
#          |
#          |
#       User documents
#
# Isi collection me register hone wale users save honge


predictions_collection = db["predictions"]





# Test connection
try:
    # Connection check karne ke liye try block start


    client.admin.command("ping")
    # MongoDB ko ping request bhej raha hai
    # Agar response mil gaya to connection successful hai




    print("MongoDB Connected Successfully")
    # Terminal me message show karega
    # Matlab MongoDB properly connect ho gaya




except Exception as e:
    # Agar MongoDB connect na ho sake
    # To error yahan handle hoga


    print("MongoDB Connection Failed")
    # Connection fail ka message show karega



    print(e)
    # Actual error detail print karega

    