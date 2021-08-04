import hmac
import sqlite3
import datetime

from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


users = fetch_users()


def init_user_table():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_product_table():
    with sqlite3.connect('products.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "title TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "category TEXT NOT NULL"
                     "date_created TEXT NOT NULL)")
    print("blog table created successfully.")


init_user_table()
init_product_table()

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


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/add-product/', methods=["POST"])
@jwt_required()
def add_product():
    response = {}

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        date_created = datetime.datetime.now()

        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO post("
                           "title,"
                           "description,"
                           "price,"
                           "category,"
                           "date_created) VALUES(?, ?, ?, ?, ?)", (title, description, price, category, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response


@app.route('/get-cart/', methods=["GET"])
def get_cart():
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response


@app.route("/remove-product/<int:product_id>")
@jwt_required()
def remove_product(product_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product removed successfully."
    return response

if __name__ == "__main__":
    app.run()