# import mysql.connector
# from Config import db_config
from pymongo import MongoClient
from Config import MONGO_URI, MONGO_DB_NAME

# --- MONGODB SETUP (ACTIVE) ---
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def get_db():
    """Returns the MongoDB database instance."""
    return db

# --- MYSQL SETUP (COMMENTED OUT AS REQUESTED) ---
"""
def get_db_connection():
    return mysql.connector.connect(**db_config)

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
    except Exception as e:
        print(f"❌ Query Error: {e}")
        result = None
    finally:
        cursor.close()
        conn.close()

    return result
"""
