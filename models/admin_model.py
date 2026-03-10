from db.database import get_db
# from db.database import get_db_connection

# 🔍 Fetch admin by email — used for login authentication
def get_admin_by_email(email):
    db = get_db()
    admin = db.admins.find_one({"email": email})
    if admin:
        admin['id'] = str(admin['_id'])
    return admin

"""
def get_admin_by_email_mysql(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email, password_hash FROM admins WHERE email = %s", (email,))
    admin = cur.fetchone()
    cur.close()
    conn.close()
    return admin
"""

# 📝 Register a new admin (optional utility)
def register_admin(name, email, hashed_password):
    db = get_db()
    db.admins.insert_one({
        "name": name,
        "email": email,
        "password_hash": hashed_password,
        "role": "admin"
    })

"""
def register_admin_mysql(name, email, hashed_password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(\"\"\"
        INSERT INTO admins (name, email, password_hash)
        VALUES (%s, %s, %s)
    \"\"\", (name, email, hashed_password))
    conn.commit()
    cur.close()
    conn.close()
"""
