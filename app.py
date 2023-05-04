from flask import Flask, request, jsonify
import re
import base64

app = Flask(__name__)

users = {}

def validate_user_id(user_id):
    if not (6 <= len(user_id) <= 20):
        return False
    return re.match("^[a-zA-Z0-9]+$", user_id) is not None

def validate_password(password):
    if not (8 <= len(password) <= 20):
        return False
    return re.match("^[ -~]+$", password) is not None

def authenticate_user(auth_header):
    if not auth_header or not auth_header.startswith('Basic '):
        return None

    try:
        auth_info = base64.b64decode(auth_header[6:]).decode('utf-8')
        user_id, password = auth_info.split(':', 1)
    except Exception:
        return None

    if user_id in users and users[user_id]['password'] == password:
        return user_id

    return None

@app.route('/signup', methods=['POST'])
def signup():
    user_id = request.json.get('user_id')
    password = request.json.get('password')

    if not user_id or not password:
        return jsonify({"message": "Account creation failed", "cause": "required user_id and password"}), 400

    if not validate_user_id(user_id):
        return jsonify({"message": "Account creation failed", "cause": "invalid user_id"}), 400

    if not validate_password(password):
        return jsonify({"message": "Account creation failed", "cause": "invalid password"}), 400

    if user_id in users:
        return jsonify({"message": "Account creation failed", "cause": "already same user_id is used"}), 400

    users[user_id] = {
        "password": password,
        "nickname": user_id
    }

    return jsonify({"message": "Account successfully created", "user": {"user_id": user_id, "nickname": user_id}}), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    auth_user_id = authenticate_user(request.headers.get('Authorization'))
    if auth_user_id is None:
        return jsonify({"message": "Authentication Failed"}), 401

    if user_id != auth_user_id:
        return jsonify({"message": "Forbidden"}), 403

    user = users.get(user_id)
    if user is None:
        return jsonify({"message": "No user found"}), 404

    response = {
        "message": "user details by user_id",
        "user": {
            "user_id": user_id,
            "nickname": user["nickname"],
            "comment": user["comment"] if "comment" in user else ""
        }
    }
    return jsonify(response), 200

@app.route('/users/<user_id>', methods=['PATCH'])
def patch_user(user_id):
    auth_user_id = authenticate_user(request.headers.get('Authorization'))
    if auth_user_id is None:
        return jsonify({"message": "Authentication Failed"}), 401

    if auth_user_id != user_id:
        return jsonify({"message": "Forbidden"}), 403

    if user_id not in users:
        return jsonify({"message": "No user found"}), 404

    data = request.get_json()

    if "user_id" in data or "password" in data:
        return jsonify({"message": "user updation failed", "cause": "not updatable user_id and password"}), 400

    if "nickname" not in data and "comment" not in data:
        return jsonify({"message": "user updation failed", "cause": "required nickname or comment"}), 400

    if "nickname" in data:
        if len(data["nickname"]) > 30:
            return jsonify({"message": "user updation failed", "cause": "nickname is too long"}), 400
        users[user_id]["nickname"] = data["nickname"] or user_id

    if "comment" in data:
        if len(data["comment"]) > 100:
            return jsonify({"message": "user updation failed", "cause": "comment is too long"}), 400
        users[user_id]["comment"] = data["comment"]

    user = users[user_id]
    return jsonify({
        "message": "user successfully updated",
        "user": {
            "nickname": user.get("nickname", user_id),
            "comment": user.get("comment", "")
        }
    }), 200

@app.route('/close', methods=['POST'])
def close_account():
    auth_user_id = authenticate_user(request.headers.get('Authorization'))
    if auth_user_id is None:
        return jsonify({"message": "Authentication Failed"}), 401

    del users[auth_user_id]

    return jsonify({"message": "Account and user successfully removed"}), 200

if __name__ == '__main__':
    app.run()
