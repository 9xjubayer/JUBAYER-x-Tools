from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "mahir_secret_key"

# MongoDB Connection (নিচে আপনার নিজের কানেকশন স্ট্রিং বসাবেন)
# এটি একটি ফ্রি ক্লাউড ডাটাবেস, যা আপনি MongoDB Atlas থেকে পাবেন।
MONGO_URI = "আপনার_মোঙ্গোডিবি_লিঙ্ক_এখানে" 
client = MongoClient(MONGO_URI)
db = client['j_tools_db']
collection = db['config']

def get_db_data():
    data = collection.find_one({"type": "main_config"})
    if not data:
        # ডিফল্ট ডাটা যদি ডাটাবেস খালি থাকে
        default_data = {
            "type": "main_config",
            "admin_password": "MAHIR00",
            "images": [],
            "total_views": 0
        }
        collection.insert_one(default_data)
        return default_data
    return data

@app.route('/')
def home():
    # ভিউ কাউন্ট আপডেট করা
    collection.update_one({"type": "main_config"}, {"$inc": {"total_views": 1}})
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
    collection.update_one({"type": "main_config"}, {"$set": {"admin_password": new_pass}})
    return jsonify({"success": True})

@app.route('/api/add', methods=['POST'])
def add_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    new_img = request.json
    collection.update_one({"type": "main_config"}, {"$push": {"images": new_img}})
    return jsonify({"success": True})

@app.route('/api/delete', methods=['POST'])
def delete_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    idx = request.json.get('index')
    data = get_db_data()
    images = data['images']
    if 0 <= idx < len(images):
        images.pop(idx)
        collection.update_one({"type": "main_config"}, {"$set": {"images": images}})
    return jsonify({"success": True})

@app.route('/api/logout')
def logout():
    session.pop('is_admin', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
def login():
    db = load_db()
    if request.json.get('password') == db['admin_password']:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/change_pass', methods=['POST'])
def change_pass():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    db = load_db()
    new_pass = request.json.get('new_password')
    if new_pass:
        db['admin_password'] = new_pass
        save_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/add', methods=['POST'])
def add_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    db = load_db()
    db['images'].append(request.json)
    save_db(db)
    return jsonify({"success": True})

@app.route('/api/delete', methods=['POST'])
def delete_image():
    if not session.get('is_admin'): return jsonify({"error": "Unauthorized"}), 403
    db = load_db()
    idx = request.json.get('index')
    if 0 <= idx < len(db['images']):
        db['images'].pop(idx)
        save_db(db)
    return jsonify({"success": True})

@app.route('/api/logout')
def logout():
    session.pop('is_admin', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
