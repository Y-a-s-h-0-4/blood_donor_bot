import pymongo
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
donors_collection = db[MONGO_COLLECTION_NAME]

def register_donor(donor_data):
    donors_collection.insert_one(donor_data)

def get_donors(blood_group):
    return donors_collection.find({"blood_group": blood_group})