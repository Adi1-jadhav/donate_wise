from db.database import get_db
# from db.database import get_db_connection

def get_user_by_email(email):
    db = get_db()
    user = db.users.find_one({"email": email})
    if user:
        user['id'] = str(user['_id']) # Maintain compatibility with .id access
    return user

"""
def get_user_by_email_mysql(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user
"""

def register_user(name, email, password_hash):
    db = get_db()
    db.users.insert_one({
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": "donor"
    })

"""
def register_user_mysql(name, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name, email, password_hash))
    conn.commit()
    conn.close()
"""
