# routes.py
# Combined, audited REST API endpoints for Tanglaw (Phase 2)
# - Register user / counselor (separate)
# - Login
# - List users (anonymous aliases)
# - Messages (GET history, POST send)
# - Appointments (create, list, update status)

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection
import datetime

api = Blueprint("api", __name__)

# ------------------------------
# HELPERS
# ------------------------------
def safe_close(cur, conn):
    """Close cursor and connection if open (helper)."""
    try:
        if cur:
            cur.close()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass

# ------------------------------
# REGISTER: normal user
# ------------------------------
@api.route("/api/register_user", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # check username exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        hashed_pw = generate_password_hash(password)
        # insert with role = 'user'
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_pw, "user")
        )
        conn.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

# ------------------------------
# REGISTER: counselor (requires code)
# ------------------------------
@api.route("/api/register_counselor", methods=["POST"])
def register_counselor():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    counselor_code = (data.get("code") or "").strip()

    if not username or not password or not counselor_code:
        return jsonify({"error": "Missing fields (username, password, code required)"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # validate counselor code
        cur.execute("SELECT id, is_used FROM counselor_codes WHERE code = %s", (counselor_code,))
        code_row = cur.fetchone()
        if not code_row:
            return jsonify({"error": "Invalid counselor code"}), 400
        if code_row.get("is_used"):
            return jsonify({"error": "Counselor code already used"}), 400

        # check username exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        hashed_pw = generate_password_hash(password)

        # insert as counselor
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_pw, "counselor")
        )

        # mark code used
        cur.execute("UPDATE counselor_codes SET is_used = 1 WHERE id = %s", (code_row["id"],))

        conn.commit()
        return jsonify({"message": "Counselor registered successfully"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

# ------------------------------
# LOGIN
# ------------------------------
@api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT id, username, password, role, created_at FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # success - return minimal safe user info
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"]
            }
        }), 200
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

# ------------------------------
# LIST USERS (anonymous aliases)
# ------------------------------
@api.route("/api/users", methods=["GET"])
def list_users():
    """
    Returns simplified list of users with anonymous aliases.
    Optional query param: exclude_id (int) to exclude requester
    """
    exclude_id = request.args.get("exclude_id", type=int)
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, role, created_at FROM users")
        rows = cur.fetchall()
        result = []
        for r in rows:
            if exclude_id and r["id"] == exclude_id:
                continue
            if r["role"] == "counselor":
                alias = f"Counselor{r['id']}"
            else:
                alias = f"Anonymous{r['id']}"
            result.append({
                "id": r["id"],
                "alias": alias,
                "role": r["role"]
            })
        return jsonify({"users": result}), 200
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

# ------------------------------
# MESSAGES
# ------------------------------
@api.route("/api/messages", methods=["GET"])
def get_messages():
    """
    Query params: from_id (requester), to_id (other)
    Example: /api/messages?from_id=3&to_id=5
    """
    from_id = request.args.get("from_id", type=int)
    to_id = request.args.get("to_id", type=int)
    if not from_id or not to_id:
        return jsonify({"message": "from_id and to_id are required"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, sender_id, receiver_id, content, timestamp, is_peer_support
            FROM messages
            WHERE (sender_id=%s AND receiver_id=%s)
               OR (sender_id=%s AND receiver_id=%s)
            ORDER BY timestamp ASC
        """, (from_id, to_id, to_id, from_id))
        rows = cur.fetchall()
        return jsonify({"messages": rows}), 200
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

@api.route("/api/messages", methods=["POST"])
def post_message():
    """
    Body JSON:
    {
      "sender_id": int,
      "receiver_id": int,
      "content": str,
      "is_peer_support": bool (optional)
    }
    """
    data = request.get_json() or {}
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = (data.get("content") or "").strip()
    is_peer_support = bool(data.get("is_peer_support", 0))

    if not sender_id or not receiver_id or not content:
        return jsonify({"message": "sender_id, receiver_id, and content are required"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, is_peer_support)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, content, int(is_peer_support)))
        conn.commit()
        return jsonify({"message": "Message sent"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

# ------------------------------
# APPOINTMENTS
# ------------------------------
@api.route("/api/appointments", methods=["POST"])
def create_appointment():
    """
    Body: { user_id, counselor_id, date (YYYY-MM-DD), time (HH:MM or HH:MM:SS) }
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    counselor_id = data.get("counselor_id")
    date_str = data.get("date")
    time_str = data.get("time")

    if not user_id or not counselor_id or not date_str or not time_str:
        return jsonify({"message": "user_id, counselor_id, date, time are required"}), 400

    try:
        _date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        try:
            _time = datetime.datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            _time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    except Exception as e:
        return jsonify({"message": "Invalid date/time format", "error": str(e)}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Optional: verify that counselor_id belongs to a counselor
        cur.execute("SELECT role FROM users WHERE id = %s", (counselor_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Counselor not found"}), 404
        # if DB returns tuple (non-dict cursor), row[0] is role OR if dict, row['role']
        role_val = row[0] if isinstance(row, tuple) else row.get("role")
        if role_val != "counselor":
            return jsonify({"message": "Selected user is not a counselor"}), 400

        cur.execute("""
            INSERT INTO appointments (user_id, counselor_id, date, time)
            VALUES (%s, %s, %s, %s)
        """, (user_id, counselor_id, _date, _time))
        conn.commit()
        return jsonify({"message": "Appointment requested"}), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)

@api.route("/api/appointments", methods=["GET"])
def get_appointments():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.id, a.user_id, a.counselor_id, a.date, a.time, a.status, 
               u.username AS user_name, c.username AS counselor_name
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN users c ON a.counselor_id = c.id
        WHERE a.user_id = %s OR a.counselor_id = %s
        ORDER BY a.date DESC, a.time DESC
    """, (user_id, user_id))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ Convert date/time fields to string to avoid timedelta serialization issue
    for row in results:
        if isinstance(row.get("date"), (str, bytes)) is False:
            row["date"] = str(row["date"])
        if isinstance(row.get("time"), (str, bytes)) is False:
            row["time"] = str(row["time"])

    return jsonify({"appointments": results}), 200


@api.route("/api/appointments/<int:appt_id>/status", methods=["PUT"])
def update_appointment_status(appt_id):
    """
    Body JSON: { "status": "pending"|'approved'|'completed'|'cancelled' }
    """
    data = request.get_json() or {}
    status = data.get("status")
    if not status or status not in ("pending", "approved", "completed", "cancelled"):
        return jsonify({"message": "Invalid status"}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, appt_id))
        conn.commit()
        return jsonify({"message": "Appointment status updated"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    finally:
        safe_close(cur, conn)
