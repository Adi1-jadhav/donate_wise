from db.database import get_db
# from db.database import get_db_connection
from datetime import datetime
from bson import ObjectId

def register_ngo(org_name, contact_email, location, mission, password_hash, verified=False):
    db = get_db()
    db.ngos.insert_one({
        "org_name": org_name,
        "contact_email": contact_email,
        "location": location,
        "mission": mission,
        "password_hash": password_hash,
        "status": "Approved" if verified else "Pending",
        "created_at": datetime.now()
    })

"""
def register_ngo_mysql(org_name, contact_email, location, mission, password_hash, verified=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(\"\"\"
        INSERT INTO ngos (org_name, contact_email, location, mission, password_hash, verified, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    \"\"\", (org_name, contact_email, location, mission, password_hash, verified, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
"""

def get_ngo_profile(ngo_id):
    db = get_db()
    try:
        ngo = db.ngos.find_one({"_id": ObjectId(ngo_id)})
        if ngo:
            ngo['id'] = str(ngo['_id'])
        return ngo
    except:
        return None

"""
def get_ngo_profile_mysql(ngo_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE id = %s", (ngo_id,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()
    return ngo
"""

def get_all_ngos():
    db = get_db()
    ngos = list(db.ngos.find().sort("created_at", -1))
    for n in ngos:
        n['id'] = str(n['_id'])
    return ngos

"""
def get_all_ngos_mysql():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ngos ORDER BY created_at DESC")
    ngos = cur.fetchall()
    cur.close()
    conn.close()
    return ngos
"""

def get_ngo_by_email(email):
    db = get_db()
    ngo = db.ngos.find_one({"contact_email": email})
    if ngo:
        ngo['id'] = str(ngo['_id'])
    return ngo

"""
def get_ngo_by_email_mysql(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE contact_email = %s", (email,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()
    return ngo
"""

