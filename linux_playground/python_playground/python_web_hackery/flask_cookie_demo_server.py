"""
Demo Flask server showing: Cookies vs Storage Values (manual headers/params)
Run this first, then run flask_cookie_demo_client.py
"""
from flask import Flask, request, make_response, jsonify
import uuid
import hashlib

app = Flask(__name__)

# Server-side session storage (dict in memory)
SESSIONS = {}

# Fake user database — starts empty, users register themselves
USERS = {}
next_user_id = 1


def hash_password(password):
    """Hash password with SHA-256. In production use bcrypt instead."""
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/register", methods=["POST"])
def register():
    """
    Best practice register:
    1. POST method (never GET — password in URL would appear in logs)
    2. Expect JSON body with username, password, name
    3. Hash the password before storing
    4. Check for duplicate username
    5. Return proper status codes
    """
    global next_user_id

    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password", "name")):
        return jsonify({"error": "Missing fields: username, password, name"}), 400

    username = data["username"]
    password = data["password"]
    name = data["name"]

    # Check if user already exists
    if username in USERS:
        return jsonify({"error": f"User '{username}' already exists"}), 409

    # Store user with HASHED password — never plaintext
    USERS[username] = {
        "user_id": next_user_id,
        "password_hash": hash_password(password),
        "name": name,
        "cart": []
    }
    next_user_id += 1

    print(f"[REGISTER] New user: {username} (ID: {USERS[username]['user_id']})")
    print(f"  Password hash: {USERS[username]['password_hash'][:16]}...")
    print(f"  Total users: {len(USERS)}")

    return jsonify({"message": f"User '{username}' registered", "user_id": USERS[username]["user_id"]}), 201


@app.route("/login", methods=["POST"])
def login():
    """
    Best practice login:
    1. POST method
    2. Verify password by comparing hashes
    3. Create session only if password matches
    """
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Missing fields: username, password"}), 400

    username = data["username"]
    password = data["password"]

    # Check user exists
    if username not in USERS:
        return jsonify({"error": "Invalid username or password"}), 401

    # Verify password hash
    if USERS[username]["password_hash"] != hash_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create session
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "user_id": USERS[username]["user_id"],
        "username": username,
        "name": USERS[username]["name"],
        "cart": []
    }

    resp = make_response(jsonify({"message": f"Welcome back, {USERS[username]['name']}!"}))
    resp.set_cookie("session_id", session_id, httponly=True)
    return resp


@app.route("/dashboard")
def dashboard():
    session_cookie = request.cookies.get("session_id")

    # ===== AUTHENTICATION CHECK =====
    if not session_cookie or session_cookie not in SESSIONS:
        return "401 Unauthorized - No valid session", 401

    # Get user data from session
    user_session = SESSIONS[session_cookie]

    print("=" * 70)
    print(f"✓ AUTHENTICATED USER: {user_session['name']}")
    print("=" * 70)
    print(f"  Session ID: {session_cookie}")
    print(f"  User ID: {user_session['user_id']}")
    print(f"  Username: {user_session['username']}")
    print(f"  Cart: {user_session['cart']}")
    print()
    print("ALL SESSIONS ON SERVER:")
    for sid, data in SESSIONS.items():
        print(f"  {sid[:8]}... → {data['name']} (ID: {data['user_id']})")
    print("=" * 70)

    return (
        f"Welcome {user_session['name']}!\n"
        f"Your user ID: {user_session['user_id']}\n"
        f"Your cart: {user_session['cart']}\n"
    )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
