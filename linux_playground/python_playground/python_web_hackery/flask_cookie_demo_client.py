"""
Demo client showing: Register → Login → Dashboard (full flow)
Run flask_cookie_demo_server.py first!
"""
import requests

BASE = "http://localhost:5555"


print("\n" + "=" * 70)
print("STEP 1: REGISTER users (POST with JSON body)")
print("=" * 70)

for user in [
    {"username": "eden", "password": "pass123", "name": "Eden"},
    {"username": "dana", "password": "pass456", "name": "Dana"},
    {"username": "nir", "password": "pass789", "name": "Nir"},
]:
    res = requests.post(f"{BASE}/register", json=user)
    print(f"  Register {user['username']}: {res.status_code} - {res.json()}")

# Try duplicate
res = requests.post(f"{BASE}/register", json={"username": "eden", "password": "x", "name": "x"})
print(f"  Duplicate eden: {res.status_code} - {res.json()}")


print("\n" + "=" * 70)
print("STEP 2: LOGIN with wrong password")
print("=" * 70)

res = requests.post(f"{BASE}/login", json={"username": "eden", "password": "WRONG"})
print(f"  Wrong password: {res.status_code} - {res.json()}")


print("\n" + "=" * 70)
print("STEP 3: LOGIN + DASHBOARD (with Session)")
print("=" * 70)

for user in [
    {"username": "eden", "password": "pass123"},
    {"username": "dana", "password": "pass456"},
    {"username": "nir", "password": "pass789"},
]:
    s = requests.Session()

    # Login — server sets cookie, Session stores it
    res = s.post(f"{BASE}/login", json=user)
    print(f"\n  Login {user['username']}: {res.status_code} - {res.json()}")
    print(f"  Session cookie: {dict(s.cookies)}")

    # Dashboard — Session sends cookie automatically
    res = s.get(f"{BASE}/dashboard")
    print(f"  Dashboard: {res.text.split(chr(10))[0]}")


print("\n" + "=" * 70)
print("STEP 4: Dashboard WITHOUT login (should fail)")
print("=" * 70)

res = requests.get(f"{BASE}/dashboard")
print(f"  No cookie: {res.status_code} - {res.text}")


if __name__ == "__main__":
    pass
