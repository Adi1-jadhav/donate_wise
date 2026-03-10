from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.donation_model import get_all_donations, get_category_stats
# from db.database import get_db_connection

admin_bp = Blueprint('admin', __name__)  # ✅ Clear, non-conflicting name

@admin_bp.route('/dashboard')
def admin_dashboard():
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    db = get_db()
    
    # 📊 Category stats
    stats = get_category_stats()

    # 📦 All donations
    donations = get_all_donations()

    # 👥 Pending NGOs
    pending_ngos = list(db.ngos.find({"status": "Pending"}))
    for ngo in pending_ngos:
        ngo['id'] = str(ngo['_id'])

    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 📊 Category stats
    cur.execute("SELECT predicted_category, COUNT(*) AS count FROM donations GROUP BY predicted_category")
    raw_stats = cur.fetchall()
    stats = {row['predicted_category']: row['count'] for row in raw_stats}

    # 📦 All donations
    cur.execute("SELECT * FROM donations")
    donations = cur.fetchall()

    # 👥 Pending NGOs (status trimmed + lowercased for safety)
    cur.execute("SELECT * FROM ngos WHERE TRIM(LOWER(status)) = 'pending'")
    pending_ngos = cur.fetchall()

    cur.close()
    conn.close()
    """

    return render_template(
        'dashboard.html',
        stats=stats,
        donations=donations,
        pending_ngos=pending_ngos
    )

@admin_bp.route('/approve_ngo/<string:ngo_id>')
def approve_ngo(ngo_id):
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    from bson import ObjectId
    db = get_db()
    db.ngos.update_one({"_id": ObjectId(ngo_id)}, {"$set": {"status": "Approved"}})
    
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ngos SET status = 'Approved' WHERE id = %s", (ngo_id,))
    conn.commit()
    cur.close()
    conn.close()
    """
    print(f"✅ NGO approved: {ngo_id}")
    flash("✅ NGO approved.")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/reject_ngo/<string:ngo_id>')
def reject_ngo(ngo_id):
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    from bson import ObjectId
    db = get_db()
    db.ngos.update_one({"_id": ObjectId(ngo_id)}, {"$set": {"status": "Rejected"}})

    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ngos SET status = 'Rejected' WHERE id = %s", (ngo_id,))
    conn.commit()
    cur.close()
    conn.close()
    """
    print(f"❌ NGO rejected: {ngo_id}")
    flash("❌ NGO rejected.")
    return redirect(url_for('admin.admin_dashboard'))
