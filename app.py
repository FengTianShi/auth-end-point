from flask import Flask, request, jsonify, abort, make_response
import re
import base64

app = Flask(__name__)

accounts = {}


def basic_auth(username, password, required_user_id=None):
    if required_user_id and required_user_id != username:
        abort(403)
    if username in accounts and accounts[username]['password'] == password:
        return True
    else:
        abort(401)


@app.route('/signup', methods=['POST'])
def signup():
    if not request.json or 'user_id' not in request.json or 'password' not in request.json:
        abort(400, description="required user_id and password")

    user_id = request.json['user_id']
    password = request.json['password']

    if not (6 <= len(user_id) <= 20) or not re.match(r'^\w+$', user_id):
        abort(400, description="length or pattern of user_id is not valid")

    if not (8 <= len(password) <= 20) or not re.match(r'^[\x21-\x7E]+$', password):
        abort(400, description="length or pattern of password is not valid")

    if user_id in accounts:
        abort(400, description="already same user_id is used")

    accounts[user_id] = {
        "user_id": user_id,
        "password": password,
        "nickname": user_id,
        "comment": ""
    }

    return jsonify({"message": "Account successfully created", "user": {"user_id": user_id, "nickname": user_id}}), 200


@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    auth = request.authorization
    if not auth:
        abort(401)

    basic_auth(auth.username, auth.password, user_id)

    if user_id not in accounts:
        abort(404, description="No user found")

    user = accounts[user_id]
    return jsonify({"message": "user details by user_id",
                    "user": {"user_id": user["user_id"], "nickname": user["nickname"], "comment": user["comment"]}})


@app.route('/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
    auth = request.authorization
    if not auth:
        abort(401)

    basic_auth(auth.username, auth.password, user_id)

    if user_id not in accounts:
        abort(404, description="No user found")

    if not request.json:
        abort(400, description="required nickname or comment")

    user = accounts[user_id]

    if 'nickname' in request.json:
        new_nickname = request.json['nickname']
        if len(new_nickname) <= 30:
            user['nickname'] = new_nickname if new_nickname else user_id

    if 'comment' in request.json:
        new_comment = request.json['comment']
        if len(new_comment) <= 100:
            user['comment'] = new_comment

    return jsonify({"message": "user successfully updated",
                    "user": {"nickname": user["nickname"], "comment": user["comment"]}}), 200


