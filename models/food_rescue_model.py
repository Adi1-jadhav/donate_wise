from db.database import get_db
from bson import ObjectId
from datetime import datetime

def post_food_rescue(donor_id, event_type, food_type, quantity_persons, address, contact_number, best_before_hours, pledge_accepted):
    db = get_db()
    
    rescue_doc = {
        "donor_id": str(donor_id),
        "event_type": event_type,
        "food_type": food_type,
        "quantity_persons": int(quantity_persons),
        "address": address,
        "contact_number": contact_number,
        "best_before_hours": float(best_before_hours),
        "pledge_accepted": pledge_accepted,
        "status": "Urgent", # Urgent, Claimed, Picked_Up
        "created_at": datetime.now(),
        "claimed_by": None,
        "claimed_at": None,
        "picked_up_at": None
    }
    
    result = db.food_rescues.insert_one(rescue_doc)
    return str(result.inserted_id)

def get_active_rescues():
    db = get_db()
    records = list(db.food_rescues.find({"status": "Urgent"}).sort("created_at", -1))
    
    for d in records:
        d['id'] = str(d['_id'])
        del d['_id']
        if 'created_at' in d: d['created_at_fmt'] = d['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate time remaining
        if 'created_at' in d and 'best_before_hours' in d:
            time_diff = (datetime.now() - d['created_at']).total_seconds() / 3600
            remaining = float(d['best_before_hours']) - time_diff
            d['hours_remaining'] = round(remaining, 1) if remaining > 0 else 0
            d['is_expired'] = remaining <= 0
        
        # Lookup donor
        user = db.users.find_one({"_id": ObjectId(d['donor_id'])}) if d.get('donor_id') else None
        d['donor_name'] = user['name'] if user else "Anonymous Donor"
        d['donor_email'] = user['email'] if user else "Unknown"

    return records

def get_rescues_by_ngo(ngo_id):
    db = get_db()
    records = list(db.food_rescues.find({"claimed_by": str(ngo_id)}).sort("claimed_at", -1))
    
    for d in records:
        d['id'] = str(d['_id'])
        del d['_id']
        
        user = db.users.find_one({"_id": ObjectId(d['donor_id'])}) if d.get('donor_id') else None
        d['donor_name'] = user['name'] if user else "Anonymous Donor"
        
    return records

def claim_food_rescue(rescue_id, ngo_id, eta_minutes):
    db = get_db()
    db.food_rescues.update_one(
        {"_id": ObjectId(rescue_id)},
        {"$set": {
            "status": "Claimed",
            "claimed_by": str(ngo_id),
            "claimed_at": datetime.now(),
            "eta_minutes": eta_minutes
        }}
    )

def mark_food_picked_up(rescue_id):
    db = get_db()
    db.food_rescues.update_one(
        {"_id": ObjectId(rescue_id)},
        {"$set": {
            "status": "Picked_Up",
            "picked_up_at": datetime.now()
        }}
    )
