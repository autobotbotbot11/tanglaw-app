from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection

routes = Blueprint('routes', __name__)

@routes.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    counselor_code = data.get('counselor_code', None)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        return jsonify({'message': 'Username already exists'}), 400

    role = 'user'

    if counselor_code:
        cur.execute("SELECT * FROM counselor_codes WHERE code=%s AND is_used=0", (counselor_code,))
        code_row = cur.fetchone()
        if not code_row:
            return jsonify({'message': 'Invalid or already used counselor code'}), 400
        role = 'counselor'
        cur.execute("UPDATE counselor_codes SET is_used=1 WHERE code=%s", (counselor_code,))

    hashed_pw = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                (username, hashed_pw, role))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({'message': 'Registered successfully', 'role': role}), 201


@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful', 'role': user['role']}), 200
