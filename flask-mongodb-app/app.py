# app.py (snippet - replace existing MongoClient init)
import os
from urllib.parse import quote_plus
from pymongo import MongoClient
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo-svc")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = os.environ.get("MONGO_DB", "flask_db")
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")

if MONGO_USER and MONGO_PASS:
    user = quote_plus(MONGO_USER)
    pwd = quote_plus(MONGO_PASS)
    mongo_uri = f"mongodb://{user}:{pwd}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
else:
    mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = client.get_database(MONGO_DB)
collection = db.get_collection("data")

@app.route("/")
def index():
    return f"Welcome to the Flask app! The current time is: {datetime.now()}"

@app.route("/data", methods=["GET","POST"])
def data_route():
    if request.method == "POST":
        payload = request.get_json()
        if not isinstance(payload, dict):
            return {"error":"Invalid JSON"}, 400
        payload["created_at"] = datetime.now().isoformat()
        collection.insert_one(payload)
        return {"status":"Data inserted"}, 201
    docs = []
    for d in collection.find({}, {"_id":0}):
        docs.append(d)
    return jsonify(docs), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
