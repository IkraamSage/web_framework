import hmac
import sqlite3

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('POS.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


def init_user_table():
    conn = sqlite3.connect('POS.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_products_table():
    with sqlite3.connect('POS.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "title TEXT NOT NULL,"
                     "content TEXT NOT NULL,"
                     "price TEXT NOT NULL)")
    print("product table created successfully.")


init_user_table()
init_products_table()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("POS.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "name,"
                           "username,"
                           "password) VALUES(?, ?, ?)", (name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


if __name__ == "__main__":
    app.debug = True
    app.run()
