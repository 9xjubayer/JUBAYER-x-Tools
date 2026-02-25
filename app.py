from flask import Flask, render_template, request, jsonify, session
import json
import os

app = Flask(__name__)
app.secret_key = "mahir_nexus_ultra_secure_key"

DATA_PATH = 'data/config.json'

def load_db():
    if not os.path.exists(DATA_PATH):
        return {"admin_password": "MAHIR00", "images": [], "total_views": 0}
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    db = load_db()
    db['total_views'] += 1
    save_db(db)
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    db = load_db()
    return jsonify({
        "images": db['images'],
        "is_admin": session.get('is_admin', False),
        "total_views": db['total_views']
    })

@app.route('/api/login', methods=['POST'])
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
