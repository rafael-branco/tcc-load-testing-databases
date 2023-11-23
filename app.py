from flask import Flask, jsonify, request
import mysql.connector
import random

app = Flask(__name__)

# Establish a connection to MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="load_testing"
)

# Create a cursor object to interact with the database
cursor = db_connection.cursor()

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Retrieve user from the MySQL database
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        user = {"id": user_data[0], "name": user_data[1], "email": user_data[2]}
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404
    

@app.route('/api/user/random', methods=['GET'])
def get_random_user():
    # Retrieve a random user from the MySQL database
    query = 'SELECT * FROM users ORDER BY RAND() LIMIT 1'
    cursor.execute(query)
    user_data = cursor.fetchone()

    if user_data:
        user = {"id": user_data[0], "name": user_data[1], "email": user_data[2]}
        return jsonify(user)
    else:
        return jsonify({"error": "No existing users"}), 404
    

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.json

    # Insert the new user into the MySQL database
    insert_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    insert_values = (data["name"], data["email"])
    cursor.execute(insert_query, insert_values)
    db_connection.commit()

    # Retrieve the auto-generated ID of the new user
    new_user_id = cursor.lastrowid

    return jsonify({"message": "User created successfully", "user_id": new_user_id})

@app.route('/api/bulk/user', methods=['POST'])
def create_bulk_users():
    data = request.json

    # Validate that the request contains a list of users
    if not isinstance(data, list):
        return jsonify({"error": "Invalid request format"}), 400

    # Insert the new users into the MySQL database using executemany
    insert_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    insert_values = [(user["name"], user["email"]) for user in data]

    try:
        cursor.executemany(insert_query, insert_values)
        db_connection.commit()
        return jsonify({"message": f"{len(data)} users created successfully"})
    except Exception as e:
        db_connection.rollback()
        return jsonify({"error": f"Failed to insert users. {str(e)}"}), 500

@app.route('/api/user/random', methods=['PUT'])
def update_user():
    data = request.json

    # Select a random existing user
    check_query = 'SELECT * FROM users ORDER BY RAND() LIMIT 1'
    cursor.execute(check_query)
    existing_user = cursor.fetchone()

    if existing_user:
        user_id = existing_user[0]  # Assuming the user ID is in the first column
        # Update the user data in the MySQL database
        update_query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
        update_values = (data["name"], data["email"], user_id)
        cursor.execute(update_query, update_values)
        db_connection.commit()

        return jsonify({"message": "User updated successfully"})
    else:
        return jsonify({"error": "No existing users"}), 404

@app.route('/api/user/random', methods=['DELETE'])
def delete_user():
    # Select a random existing user
    check_query = 'SELECT * FROM users ORDER BY RAND() LIMIT 1'
    cursor.execute(check_query)
    existing_user = cursor.fetchone()

    if existing_user:
        user_id = existing_user[0]  # Assuming the user ID is in the first column
        # Delete the user from the MySQL database
        delete_query = "DELETE FROM users WHERE id = %s"
        cursor.execute(delete_query, (user_id,))
        db_connection.commit()

        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "No existing users"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
