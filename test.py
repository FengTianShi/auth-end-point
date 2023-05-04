from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    # TODO: 查询数据库以获取用户信息
    user = {'id': user_id, 'name': 'John Doe', 'email': 'john.doe@example.com'}
    return jsonify(user)

if __name__ == '__main__':
    app.run()
