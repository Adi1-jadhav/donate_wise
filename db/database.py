import mysql.connector
from Config import db_config

#🔌 Establish connection
def get_db_connection():
    return mysql.connector.connect(**db_config)
# def get_db_connection():
#     return mysql.connector.connect(
#         host="yamanote.proxy.rlwy.net",
#         port=12682,
#         user="root",
#         password="VzRIoNlmOHRYWYEBoWEzVoRqceYdojoQ",
#         database="donation"
#     )

# 🧠 Execute query (SELECT / INSERT / UPDATE / DELETE)
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
