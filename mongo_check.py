from pymongo import MongoClient
try:
    c = MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=5000)
    c.admin.command('ping')
    print('Mongo reachable on 27017')
except Exception as e:
    print('Mongo connect failed:', e)
