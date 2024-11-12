from flask import Flask, request, jsonify
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import time
import os

app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/facebookdb")
client = MongoClient(MONGO_URI)
db = client.facebookdb
collection = db.posts


def fetch_facebook_posts(topic):
    search_url = f"https://www.facebook.com/search/posts/?q={topic}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return []

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts_data = []
    posts = soup.find_all('div', class_='post_class')  # Adjust this based on actual class used on Facebook
    
    for post in posts[:5]:  # Limit to the first 5 posts
        post_text = post.get_text(strip=True)
        post_url = "https://www.facebook.com" + post.find('a')['href']
        
        post_data = {
            "topic": topic,
            "content": post_text,
            "url": post_url,
            "comments": [
                {"user": "User1", "comment": "Interesting point", "timestamp": time.ctime()},
                {"user": "User2", "comment": "Needs more context", "timestamp": time.ctime()}
            ]
        }
        posts_data.append(post_data)
    
    return posts_data

# Endpoint to search posts by topic and save to MongoDB
@app.route('/sample', methods=['POST'])
def sample():
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Insert the data into MongoDB
        collection.insert_many(data)

        return jsonify({"status": "success", "message": "Sample posts inserted successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# Endpoint to search posts by topic and save to MongoDB
@app.route('/search_posts', methods=['POST'])
def search_posts():
    try:
        # Try to get JSON data first
        data = request.get_json()
        if data is None:  # If JSON data isn't present, check form data
            data = request.form

        topic = data.get("topic", "")
        if not topic:
            return jsonify({"status": "error", "message": "Topic is required"}), 400
        
        # Fetch posts based on the topic
        posts = fetch_facebook_posts(topic)
        
        if not posts:
            return jsonify({"status": "error", "message": "No posts found for the given topic"}), 404
        
        return jsonify({"status": "success", "data": posts})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to get posts of a specific topic from MongoDB
@app.route('/get_topic_posts', methods=['GET'])
def get_topic_posts():
    topic = request.args.get('topic', None)
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # Fetch posts from MongoDB based on the topic
    posts = list(collection.find({"topic": topic}))

    # If no posts are found for the topic
    if not posts:
        return jsonify({"message": f"No posts found for topic '{topic}'"}), 404

    # Return posts in a readable format (excluding MongoDB-specific fields)
    posts_data = []
    for post in posts:
        post_data = {
            "content": post.get("content"),
            "url": post.get("url"),
            "comments": post.get("comments"),
            "reactions": post.get("reactions")
        }
        posts_data.append(post_data)
    
    return jsonify({"topic": topic, "posts": posts_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
