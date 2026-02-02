# crud_mongo.py
from pymongo import MongoClient
import json

# client = MongoClient("mongodb://localhost:27017/")
# db = client["mongoHbm"]
# musiciens = db["musiciens"]
# collections = db.list_collection_names()

def get_session():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mongoHbm"]
    return db

def close_session():
    client = MongoClient("mongodb://localhost:27017/")
    return client.close()


def read_all_musiciens():
    db=get_session()
    musiciens = db["musiciens"]
    result = list(musiciens.find({},{"instruments":0}))
    for res in result:
        res["_id"]= str(res["_id"])
    return {"musiciens":result}

# def read_musicien_by_nom():


# def read_all_musiciens():
#     result = db.musiciens.find({})
    
#     return result

print(json.dumps(read_all_musiciens(), indent=4, ensure_ascii=False))
# read_all_musiciens()
# print("Collections de la base:", collections)
close_session()