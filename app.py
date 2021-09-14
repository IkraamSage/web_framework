import hmac
import sqlite3
import datetime
# importing
from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS

# OOP for username password

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# defining functions for sqlite

def fetch_users():
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


# sqlite functions

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
# init product table

def init_product_table():
    with sqlite3.connect('products.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "title TEXT NOT NULL,"
                     "img_url TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "category TEXT NOT NULL,"
                     "date_created TEXT NOT NULL)")
    print("blog table created successfully.")


init_user_table()
init_product_table()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

# defining token functions

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
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=4000)
CORS(app)
jwt = JWT(app, authenticate, identity)

# making app route for registration

@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.json['first_name']
        last_name = request.json['last_name']
        username = request.json['username']
        password = request.json['password']

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

#   Route for the user to login.
@app.route("/user_login/", methods=["POST"])
#   Function to register user
def user_login():
    response = {}

    if request.method == "POST":
        entered_username = request.json['username']
        entered_password = request.json['password']

        with sqlite3.connect("products.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (entered_username,
                                                                                  entered_password))
            table_info = cursor.fetchone()

            response["status_code"] = 200
            response["message"] = "User logged in successfully"
            response["user"] = table_info
        return response

    else:
        response["status_code"] = 404
        response["user"] = "user not found"
        response["message"] = "User logged in unsuccessfully"
    return response

# making app route for adding products

@app.route('/add-product/', methods=["POST"])
def add_product():
    response = {}

    if request.method == "POST":
        title = request.json['title']
        img_url = request.json['img_url']
        description = request.json['description']
        price = request.json['price']
        category = request.json['category']
        date_created = datetime.datetime.now()

        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product("
                           "title,"
                           "img_url,"
                           "description,"
                           "price,"
                           "category,"
                           "date_created) VALUES(?, ?, ?, ?, ?, ?)", (title, img_url, description, price, category, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response

# defing app route for cart

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

# defining app route for removing products

@app.route("/remove-product/<int:product_id>/")
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


@app.route('/view/')
def view_products():
    response = {}

    with sqlite3.connect("products.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/updating/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('products.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET title =? WHERE id=?", (put_data["title"], product_id))
                    conn.commit()
                    response['message'] = "Update to title was successful"
                    response['status_code'] = 200
            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE id=?", (put_data["description"], product_id))
                    conn.commit()

                    response["description"] = "Update to description successful"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["price"] = "Update to price was successful"
                    response["status_code"] = 200
            if incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE id=?", (put_data["category"], product_id))
                    conn.commit()

                    response["category"] = "Update to category was successful"
                    response["status_code"] = 200
    return response


if __name__ == "__main__":
    app.run()