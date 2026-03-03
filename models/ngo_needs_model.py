from db.database import get_db_connection

def post_need(ngo_id, category, item_name, quantity, description, priority):
    """NGO posts a new urgent need."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ngo_needs (ngo_id, category, item_name, quantity, description, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (ngo_id, category, item_name, quantity, description, priority))
    conn.commit()
    cur.close()
    conn.close()

def get_ngo_active_needs(ngo_id):
    """Gets all open needs for a specific NGO."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngo_needs WHERE ngo_id = %s AND status = 'Open' ORDER BY created_at DESC", (ngo_id,))
    needs = cur.fetchall()
    cur.close()
    conn.close()
    return needs

def get_all_active_needs():
    """Gets all active needs from across all NGOs for the donor dashboard."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT n.*, o.org_name, o.location as ngo_location 
        FROM ngo_needs n
        JOIN ngos o ON n.ngo_id = o.id
        WHERE n.status = 'Open'
        ORDER BY CASE 
            WHEN priority = 'High' THEN 1 
            WHEN priority = 'Medium' THEN 2 
            ELSE 3 
        END, created_at DESC
    """)
    needs = cur.fetchall()
    cur.close()
    conn.close()
    return needs

def fulfill_need(need_id):
    """Mark a need as fulfilled."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ngo_needs SET status = 'Fulfilled' WHERE id = %s", (need_id,))
    conn.commit()
    cur.close()
    conn.close()

def delete_need(need_id, ngo_id):
    """Delete a need (only by the NGO who created it)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ngo_needs WHERE id = %s AND ngo_id = %s", (need_id, ngo_id))
    conn.commit()
    cur.close()
    conn.close()
