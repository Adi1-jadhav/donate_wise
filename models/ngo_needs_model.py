from db.database import get_db
# from db.database import get_db_connection
from datetime import datetime
from bson import ObjectId

def post_need(ngo_id, category, item_name, quantity, description, priority):
    """NGO posts a new urgent need."""
    db = get_db()
    db.ngo_needs.insert_one({
        "ngo_id": str(ngo_id),
        "category": category,
        "item_name": item_name,
        "quantity": quantity,
        "description": description,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now()
    })

"""
def post_need_mysql(ngo_id, category, item_name, quantity, description, priority):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(\"\"\"
        INSERT INTO ngo_needs (ngo_id, category, item_name, quantity, description, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    \"\"\", (ngo_id, category, item_name, quantity, description, priority))
    conn.commit()
    cur.close()
    conn.close()
"""

def get_ngo_active_needs(ngo_id):
    """Gets all open needs for a specific NGO."""
    db = get_db()
    needs = list(db.ngo_needs.find({"ngo_id": str(ngo_id), "status": "Open"}).sort("created_at", -1))
    for n in needs:
        n['id'] = str(n['_id'])
    return needs

"""
def get_ngo_active_needs_mysql(ngo_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngo_needs WHERE ngo_id = %s AND status = 'Open' ORDER BY created_at DESC", (ngo_id,))
    needs = cur.fetchall()
    cur.close()
    conn.close()
    return needs
"""

def get_all_active_needs():
    """Gets all active needs from across all NGOs for the donor dashboard."""
    db = get_db()
    needs = list(db.ngo_needs.find({"status": "Open"}))
    
    # Enrichment: In MongoDB we'd typically use lookup/aggregate or separate queries
    results = []
    for n in needs:
        n['id'] = str(n['_id'])
        # Simplified Lookup
        ngo = db.ngos.find_one({"_id": ObjectId(n['ngo_id'])})
        if ngo:
            n['org_name'] = ngo['org_name']
            n['ngo_location'] = ngo['location']
        results.append(n)
        
    # Python-side sort to maintain priority logic
    priority_map = {'High': 1, 'Medium': 2, 'Low': 3}
    results.sort(key=lambda x: (priority_map.get(x['priority'], 4), x['created_at']), reverse=False)
    
    return results

"""
def get_all_active_needs_mysql():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(\"\"\"
        SELECT n.*, o.org_name, o.location as ngo_location 
        FROM ngo_needs n
        JOIN ngos o ON n.ngo_id = o.id
        WHERE n.status = 'Open'
        ORDER BY CASE 
            WHEN priority = 'High' THEN 1 
            WHEN priority = 'Medium' THEN 2 
            ELSE 3 
        END, created_at DESC
    \"\"\", (ngo_id,))
    needs = cur.fetchall()
    cur.close()
    conn.close()
    return needs
"""

def fulfill_need(need_id):
    """Mark a need as fulfilled."""
    db = get_db()
    db.ngo_needs.update_one({"_id": ObjectId(need_id)}, {"$set": {"status": "Fulfilled"}})

"""
def fulfill_need_mysql(need_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ngo_needs SET status = 'Fulfilled' WHERE id = %s", (need_id,))
    conn.commit()
    cur.close()
    conn.close()
"""

def delete_need(need_id, ngo_id):
    """Delete a need (only by the NGO who created it)."""
    db = get_db()
    db.ngo_needs.delete_one({"_id": ObjectId(need_id), "ngo_id": str(ngo_id)})

"""
def delete_need_mysql(need_id, ngo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ngo_needs WHERE id = %s AND ngo_id = %s", (need_id, ngo_id))
    conn.commit()
    cur.close()
    conn.close()
"""
