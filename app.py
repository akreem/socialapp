from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB (using the MongoDB service name defined in Docker Compose)
client = MongoClient("mongodb://mongodb:27017/")
db = client["social_media_lab"]
collection = db["posts"]

@app.route('/add_post', methods=['POST'])
def add_post():
    data = request.json
    if data:
        collection.insert_one(data)
        return jsonify({"status": "success", "message": "Post added"}), 201
    else:
        return jsonify({"status": "error", "message": "No data provided"}), 400

@app.route('/get_posts', methods=['GET'])
def get_posts():
    posts = list(collection.find({}, {"_id": 0}))
    return jsonify(posts), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
