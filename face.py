import psycopg
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
from datetime import datetime


app = Flask(__name__)
CORS(app)

DB_HOST = "localhost"
DB_NAME = "face-detector-v1"
DB_USER = "postgres"
DB_PASSWORD = "admin"

def register_user(name, email, hashed):
    with psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as connection:
        with connection.cursor() as cursor:
            print("111111")
            cursor.execute(
                "INSERT INTO login (hash, email) VALUES (%s, %s)",
                (str(hashed), email)
            )
            print("222222")
            cursor.execute(
                "INSERT INTO users (name, email, joined) VALUES (%s, %s, %s)",
                (name, email, datetime.now())
            )
            connection.commit()
            print("Data inserted successfully!")



@app.route('/register', methods=['POST'])
def handle_register():
    # Access data from the POST request
    data = request.get_json()  # For JSON data
    if not data:
        print("xd")
        return jsonify({"error": "No data provided"}), 400

    # Process the data
    email = data.get('email', 'Unknown')
    name = data.get('name', 'Unknown')
    password = str.encode(data.get('password', 'Unknown'))
    print(password)

    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(hashed)

    try:
        register_user(name, email, hashed)
        return jsonify({
            "message": "Registered successfully",
            "name": email,
            "email": email
        })

    except:
        print("error registering user")
        return jsonify({"error": "unable to register"}), 400


def sign_user_in(email, password):
    with psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as connection:
        with connection.cursor() as cursor:
            print(email)
            print("bruhhhh")
            cursor.execute(
                "SELECT email, hash FROM login WHERE email = '" + email + "'"
            )
            print("xddddd")
            rows = cursor.fetchall()
            print(rows)
            p = str.encode(rows[0][1][2:-1])
            print(p)
            is_valid = bcrypt.checkpw(password, p)
            if is_valid:
                cursor.execute(
                    "SELECT * FROM users WHERE email = '" + email + "'"
                )
                user = cursor.fetchall()[0]
                print(user)
                return user


@app.route('/signin', methods=['POST'])
def handle_signin():
    # Access data from the POST request
    data = request.get_json()  # For JSON data
    if not data:
        print("xd")
        return jsonify({"error": "No data provided"}), 400

    # Process the data
    email = data.get('email', 'Unknown')
    password = str.encode(data.get('password', 'Unknown'))

    print(email)
    print(password)

    try:
        user = sign_user_in(email, password)
        return jsonify({
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "entries": user[3],
            "joined": user[4]
        })
    # Respond with a message
    except:
        print("error signing in user")
        return jsonify({"error": "unable to signin"}), 400

def get_user_details(id):
    with psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as connection:
        with connection.cursor() as cursor:
            print("bruhhhh")
            cursor.execute(
                "SELECT * FROM users WHERE id = '" + id + "'"
            )
            user = cursor.fetchall()[0]
            return user

@app.route('/profile', methods=['GET'])
def handle_get_user():
    print("ummmmm")

    # Process the data
    user_id = request.args.get('id')
    print(user_id)

    try:
        user = get_user_details(user_id)
        if not user:
            return jsonify({"error": "unable to get user. check id"}), 400
        return jsonify({
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "entries": user[3],
            "joined": user[4]
        })
    # Respond with a message
    except:
        print("check user id")
        return jsonify({"error": "check user id"}), 400


def increment_entries(id):
    with psycopg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as connection:
        with connection.cursor() as cursor:
            print("bruhhhh")
            cursor.execute(
                "UPDATE users SET entries = entries + 1 WHERE id =" + id
            )
            connection.commit()
            cursor.execute(
                "SELECT entries FROM users WHERE id =" + id
            )
            entries = cursor.fetchall()[0]
            return entries

@app.route('/image', methods=['PUT'])
def handle_put_image():
    print("ummmmm")
    data = request.get_json()

    # Process the data
    user_id = data.get('id')
    print(user_id)

    try:
        entries = increment_entries(user_id)
        return jsonify({
            "entries": entries
        })
    # Respond with a message
    except:
        print("check user id")
        return jsonify({"error": "check user id"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)