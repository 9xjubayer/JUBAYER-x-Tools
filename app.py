from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "jubayer_nexus_secret_key"

# --- MongoDB Setup ---
# ১. MongoDB Atlas (mongodb.com) এ ফ্রি অ্যাকাউন্ট খুলে একটি কানেকশন লিঙ্ক নিন।
# ২. নিচের লিঙ্কে আপনার ইউজারনেম ও পাসওয়ার্ড বসান।
MONGO_URI = "mongodb+srv://admin:password123@cluster0.mongodb.net/myDatabase?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client['jubayer_tools']
    collection = db['config']
except Exception as e:
    print(f"Database Connection Error: {e}")

def get_db_data():
    """ডাটাবেস থেকে কনফিগারেশন আনা"""
    data = collection.find_one({"type": "settings"})
    if not data:
        # যদি ডাটাবেস একদম খালি থাকে তবে এই ডিফল্ট ডাটা সেট হবে
        default_data = {
            "type": "settings",
            "admin_password": "MAHIR00",
            "images": [],
            "total_views": 0
        }
        collection.insert_one(default_data)
        return default_data
    return data

# --- Routes ---

@app.route('/')
def home():
    # সাইট ভিজিট করলেই ভিউ কাউন্ট ১ বাড়বে (Database Update)
    collection.update_one({"type": "settings"}, {"$inc": {"total_views": 1}})
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    data = get_db_data()
    return jsonify({
        "images": data['images'],
        "is_admin": session.get('is_admin', False),
        "total_views": data['total_views']
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = get_db_data()
    if request.json.get('password') == data['admin_password']:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/change_pass', methods=['POST'])
def change_pass():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    new_pass = request.json.get('new_password')
    if new_pass:
        collection.update_one({"type": "settings"}, {"$set": {"admin_password": new_pass}})
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/add', methods=['POST'])
def add_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    new_img = request.json
    collection.update_one({"type": "settings"}, {"$push": {"images": new_img}})
    return jsonify({"success": True})

@app.route('/api/delete', methods=['POST'])
def delete_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    idx = request.json.get('index')
    data = get_db_data()
    images = data['images']
    if 0 <= idx < len(images):
        images.pop(idx)
        collection.update_one({"type": "settings"}, {"$set": {"images": images}})
    return jsonify({"success": True})

@app.route('/api/logout')
def logout():
    session.pop('is_admin', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
