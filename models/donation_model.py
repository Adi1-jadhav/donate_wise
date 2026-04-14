# import mysql.connector
# from Config import db_config
from db.database import get_db
from models.pickup_recommender import should_recommend_pickup
from bson import ObjectId
from datetime import datetime, timedelta

# 🔍 All Donations + Donor Info
def get_all_donations():
    db = get_db()
    donations = list(db.donations.find().sort("created_at", -1))
    
    for d in donations:
        d['id'] = str(d['_id'])
        del d['_id']
        # Keep as datetime objects for Jinja2 strftime()
        # if 'created_at' in d: d['created_at'] = str(d['created_at'])
        # if 'claimed_at' in d: d['claimed_at'] = str(d['claimed_at'])
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        # Get donor name
        user = db.users.find_one({"_id": ObjectId(d['user_id'])}) if d.get('user_id') else None
        d['user_name'] = user['name'] if user else "Unknown"
        
        d['pickup_recommended'] = should_recommend_pickup(
            d.get('quantity', 0), d.get('predicted_category', ''), d.get('description', '')
        )
    return donations

# 📊 Category Stats for Filters
def get_category_stats():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$predicted_category", "count": {"$sum": 1}}}
    ]
    results = list(db.donations.aggregate(pipeline))
    return {
        (row['_id'] or "Uncategorized"): row['count']
        for row in results
    }

# 💾 Save Donation
def save_donation(user_id, title, description, location, quantity,
                  predicted_category, image_filename,
                  pickup_required=False, pickup_time=None, pickup_status=None):
    db = get_db()
    
    # Ensure safe defaults
    if pickup_status is None:
        pickup_status = 'pending'
    
    donation_doc = {
        "user_id": str(user_id),
        "title": title,
        "description": description,
        "location": location,
        "quantity": int(quantity) if str(quantity).isdigit() else 1,
        "predicted_category": predicted_category or "Uncategorized",
        "image_filename": image_filename or "",
        "pickup_required": pickup_required,
        "pickup_time": pickup_time,
        "pickup_status": pickup_status,
        "created_at": datetime.now(),
        "claimed_by": None,
        "claimed_at": None
    }
    
    result = db.donations.insert_one(donation_doc)
    print(f"✅ Donation saved with ID: {result.inserted_id}")
    return str(result.inserted_id)

# 🛠 Update Pickup Status
def update_pickup_status(donation_id, status):
    db = get_db()
    db.donations.update_one(
        {"_id": ObjectId(donation_id)},
        {"$set": {"pickup_status": status}}
    )
    print(f"✅ Pickup status updated to '{status}' for donation ID: {donation_id}")

# 📥 Unclaimed Donations
def get_unclaimed_donations():
    db = get_db()
    records = list(db.donations.find({"claimed_by": None}).sort("created_at", -1))
    
    for d in records:
        d['id'] = str(d['_id'])
        del d['_id']
        # Keep as datetime objects for template formatting
        # if 'created_at' in d: d['created_at'] = str(d['created_at'])
        # if 'claimed_at' in d: d['claimed_at'] = str(d['claimed_at'])
        # 👤 Fetch Donor Name safely
        user_id = d.get('user_id')
        user = None
        if user_id:
            try:
                user = db.users.find_one({"_id": ObjectId(user_id)})
            except:
                pass
        d['user_name'] = user['name'] if user else "Donor"
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d.get('quantity'), d.get('predicted_category'), d.get('description')
        )
    return records

# ✅ Claimed Donations by NGO
def get_claimed_donations(ngo_id):
    db = get_db()
    # In MongoDB, we can just find donations where claimed_by == ngo_id
    claimed = list(db.donations.find({"claimed_by": str(ngo_id)}).sort("claimed_at", -1))
    
    for d in claimed:
        d['id'] = str(d['_id'])
        del d['_id']
        # Keep as datetime objects for template strftime formatting
        # if 'created_at' in d: d['created_at'] = str(d['created_at'])
        # if 'claimed_at' in d: d['claimed_at'] = str(d['claimed_at'])
        # 👤 Fetch Donor Name safely
        user_id = d.get('user_id')
        user = None
        if user_id:
            try:
                user = db.users.find_one({"_id": ObjectId(user_id)})
            except:
                pass
        d['user_name'] = user['name'] if user else "Donor"
        
        ngo = db.ngos.find_one({"_id": ObjectId(ngo_id)})
        d['claimed_by_name'] = ngo['org_name'] if ngo else "NGO"
        
        # Merge claim metadata if stored separately or just use fields in donation doc
        # For simplicity, we assume metadata like 'pickup_notes' is also in the donation or linked
    return claimed

# 📍 Mark Donation as Claimed
def mark_donation_claimed(donation_id, ngo_id, pickup_time=None, pickup_notes=None):
    db = get_db()
    db.donations.update_one(
        {"_id": ObjectId(donation_id)},
        {"$set": {
            "claimed_by": str(ngo_id), 
            "claimed_at": datetime.now(),
            "scheduled_pickup_time": pickup_time,
            "pickup_notes": pickup_notes,
            "pickup_status": "Claimed"
        }}
    )

def mark_donation_fulfilled(donation_id):
    db = get_db()
    db.donations.update_one(
        {"_id": ObjectId(donation_id)},
        {"$set": {"pickup_status": "Fulfilled"}}
    )

def mark_donation_dispatched(donation_id):
    db = get_db()
    db.donations.update_one(
        {"_id": ObjectId(donation_id)},
        {"$set": {"pickup_status": "Dispatched"}}
    )

# 📧 Get Donor Info by Donation — used for notifications
def get_donor_by_donation_id(donation_id):
    db = get_db()
    try:
        donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    except Exception:
        return None
        
    if donation:
        try:
            user = db.users.find_one({"_id": ObjectId(donation['user_id'])})
        except Exception:
            user = None
            
        if user:
            return {
                "id": str(user['_id']),
                "name": user['name'],
                "email": user['email'],
                "donation_title": donation['title']
            }
    return None

# 🔍 Single Donation by ID
def get_donation_by_id(donation_id):
    db = get_db()
    d = db.donations.find_one({"_id": ObjectId(donation_id)})
    if d:
        d['id'] = str(d['_id'])
    return d

# 📊 GLOBAL IMPACT STATS
def get_impact_stats():
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": None,
            "total_items": {"$sum": "$quantity"},
            "donation_count": {"$sum": 1}
        }}
    ]
    result = list(db.donations.aggregate(pipeline))
    return result[0] if result else {'total_items': 0, 'donation_count': 0}

# 🏆 LEADERBOARD: TOP 5 DONORS
def get_top_donors():
    db = get_db()
    pipeline = [
        {"$match": {"pickup_status": "Fulfilled"}},
        {"$group": {
            "_id": "$user_id",
            "total_qty": {"$sum": "$quantity"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_qty": -1}},
        {"$limit": 5}
    ]
    results = list(db.donations.aggregate(pipeline))
    
    final = []
    for r in results:
        user = db.users.find_one({"_id": ObjectId(r['_id'])})
        final.append({
            "name": user['name'] if user else "Donor",
            "total_qty": r['total_qty'],
            "count": r['count']
        })
    return final

# 📍 MAP DATA: RECENT ACTIVITY
def get_recent_map_data():
    db = get_db()
    thirty_days_ago = datetime.now() - timedelta(days=30)
    map_data = list(db.donations.find(
        {"created_at": {"$gt": thirty_days_ago}},
        {"title": 1, "location": 1, "predicted_category": 1, "pickup_status": 1}
    ).sort("created_at", -1).limit(15))
    
    for d in map_data:
        d['id'] = str(d['_id'])
        del d['_id']
        if 'created_at' in d: d['created_at'] = str(d['created_at'])
        d['category'] = d.get('predicted_category')
        d['status'] = d.get('pickup_status')
    return map_data

# 👤 DONOR PROFILE STATS
def get_donor_profile_stats(user_id):
    db = get_db()
    
    total_donations = db.donations.count_documents({"user_id": str(user_id)})
    
    pipeline_qty = [
        {"$match": {"user_id": str(user_id)}},
        {"$group": {"_id": None, "total": {"$sum": "$quantity"}}}
    ]
    res_qty = list(db.donations.aggregate(pipeline_qty))
    total_items = res_qty[0]['total'] if res_qty else 0
    
    # By status
    status_pipeline = [
        {"$match": {"user_id": str(user_id)}},
        {"$group": {"_id": "$pickup_status", "count": {"$sum": 1}}}
    ]
    by_status = {r['_id']: r['count'] for r in db.donations.aggregate(status_pipeline)}
    
    # By category
    cat_pipeline = [
        {"$match": {"user_id": str(user_id)}},
        {"$group": {"_id": "$predicted_category", "count": {"$sum": 1}, "qty": {"$sum": "$quantity"}}},
        {"$sort": {"count": -1}}
    ]
    by_category = [{"category": r['_id'], "count": r['count'], "qty": r['qty']} for r in db.donations.aggregate(cat_pipeline)]

    return {
        'total_donations': total_donations,
        'total_items': int(total_items),
        'fulfilled': by_status.get('Fulfilled', 0),
        'dispatched': by_status.get('Dispatched', 0),
        'pending': by_status.get('Pending', 0),
        'by_category': by_category,
        'monthly': [] # Simplified for now
    }

# 🏅 DONOR BADGES
def get_donor_badges(stats):
    badges = []
    total = stats['total_items']
    fulfilled = stats['fulfilled']
    donations = stats['total_donations']
    cats = [c['category'] for c in stats['by_category']]

    if total >= 1:
        badges.append({'icon': '🌱', 'title': 'First Step', 'desc': 'Made your first donation', 'color': '#10b981'})
    if total >= 10:
        badges.append({'icon': '⭐', 'title': 'Rising Star', 'desc': '10+ items donated', 'color': '#f59e0b'})
    if total >= 50:
        badges.append({'icon': '🔥', 'title': 'On Fire', 'desc': '50+ items donated', 'color': '#ef4444'})
    if total >= 100:
        badges.append({'icon': '💎', 'title': 'Diamond Donor', 'desc': '100+ items shared', 'color': '#6366f1'})
    if fulfilled >= 1:
        badges.append({'icon': '✅', 'title': 'Mission Complete', 'desc': 'First item fully delivered', 'color': '#10b981'})
    if fulfilled >= 5:
        badges.append({'icon': '🎯', 'title': 'Impact Maker', 'desc': '5+ deliveries verified', 'color': '#2563eb'})
    if 'Food' in cats:
        badges.append({'icon': '🍱', 'title': 'Food Hero', 'desc': 'Donated food items', 'color': '#f59e0b'})
    if 'Books' in cats:
        badges.append({'icon': '📚', 'title': 'Knowledge Giver', 'desc': 'Donated books', 'color': '#8b5cf6'})
    if 'Medical' in cats:
        badges.append({'icon': '🏥', 'title': 'Health Guardian', 'desc': 'Donated medical supplies', 'color': '#ef4444'})
    if donations >= 5:
        badges.append({'icon': '🤝', 'title': 'Community Pillar', 'desc': '5+ separate donations', 'color': '#06b6d4'})

    return badges

# 📡 LIVE ACTIVITY FEED
def get_live_activity_feed(limit=10):
    db = get_db()
    donations = list(db.donations.find().sort("created_at", -1).limit(limit))
    
    events = []
    for item in donations:
        user = db.users.find_one({"_id": ObjectId(item['user_id'])}) if item.get('user_id') else None
        donor_name = user['name'] if user else "Donor"
        
        ngo = db.ngos.find_one({"_id": ObjectId(item['claimed_by'])}) if item.get('claimed_by') else None
        ngo_name = ngo['org_name'] if ngo else None

        if item['pickup_status'] == 'Fulfilled':
            events.append({
                'icon': '🎉',
                'text': f"<b>{donor_name}</b>'s {item['title']} was delivered!",
                'tag': 'Fulfilled', 'color': '#10b981', 'time': item.get('claimed_at') or item['created_at']
            })
        elif item['pickup_status'] == 'Dispatched':
            events.append({
                'icon': '🚚',
                'text': f"<b>{ngo_name or 'An NGO'}</b> is on the way to pick up {item['title']}",
                'tag': 'En Route', 'color': '#2563eb', 'time': item.get('claimed_at') or item['created_at']
            })
        elif ngo_name:
            events.append({
                'icon': '📥',
                'text': f"<b>{ngo_name}</b> claimed <b>{item['title']}</b>",
                'tag': 'Claimed', 'color': '#6366f1', 'time': item.get('claimed_at') or item['created_at']
            })
        else:
            events.append({
                'icon': '❤️',
                'text': f"<b>{donor_name}</b> donated {item['title']} ({item.get('predicted_category')})",
                'tag': 'New Donation', 'color': '#f43f5e', 'time': item['created_at']
            })
    return events

# 🔔 USER NOTIFICATIONS
def get_user_notifications(user_id):
    db = get_db()
    notifications = []
    
    # Derive from donations where status changed
    rows = list(db.donations.find({
        "user_id": str(user_id),
        "$or": [{"claimed_by": {"$ne": None}}, {"pickup_status": {"$in": ["Dispatched", "Fulfilled"]}}]
    }).sort("created_at", -1).limit(8))

    for row in rows:
        ngo = db.ngos.find_one({"_id": ObjectId(row['claimed_by'])}) if row.get('claimed_by') else None
        org_name = ngo['org_name'] if ngo else "An NGO"

        if row['pickup_status'] == 'Fulfilled':
            notifications.append({'icon': '🎉', 'title': 'Delivery Confirmed!', 'body': f"Your <b>{row['title']}</b> was delivered.", 'color': '#10b981', 'donation_id': str(row['_id']), 'time': str(row.get('claimed_at') or row['created_at'])})
        elif row['pickup_status'] == 'Dispatched':
            notifications.append({'icon': '🚚', 'title': 'On The Way!', 'body': f"<b>{org_name}</b> is picking up your <b>{row['title']}</b>.", 'color': '#2563eb', 'donation_id': str(row['_id']), 'time': str(row.get('claimed_at') or row['created_at'])})
        elif row.get('claimed_by'):
            notifications.append({'icon': '📥', 'title': 'Donation Claimed!', 'body': f"<b>{org_name}</b> has claimed your <b>{row['title']}</b>.", 'color': '#6366f1', 'donation_id': str(row['_id']), 'time': str(row.get('claimed_at') or row['created_at'])})
            
    return notifications

# --- MYSQL CODE (COMMENTED) ---
"""
# def get_all_donations_mysql():
#     conn = mysql.connector.connect(**db_config)
#     ...
"""
