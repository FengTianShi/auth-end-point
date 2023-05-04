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

if __name__ == '__main__':
    app.run()
