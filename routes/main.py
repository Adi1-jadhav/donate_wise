import os
import cloudinary
import cloudinary.uploader
from Config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from markupsafe import Markup

# Cloudinary Configuration
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)
from routes.email_utils import (
    send_claimed_notification,
    send_dispatched_notification,
    send_fulfilled_notification
)

# from db.database import get_db_connection
from models.ngo_models import register_ngo, get_ngo_profile
from ai_model.predictor import predict_category, predict_impact
from models.pickup_recommender import should_recommend_pickup
from models.donation_model import (
    get_category_stats,
    save_donation,
    get_all_donations,
    update_pickup_status,
    get_unclaimed_donations,
    get_claimed_donations,
    mark_donation_claimed,
    get_donor_by_donation_id,
    mark_donation_fulfilled,
    mark_donation_dispatched,
    get_donation_by_id,
    get_impact_stats,
    get_top_donors,
    get_recent_map_data,
    get_donor_profile_stats,
    get_donor_badges,
    get_live_activity_feed,
    get_user_notifications
)
from models.ngo_needs_model import post_need, get_ngo_active_needs, delete_need, get_all_active_needs

main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')

@main.route('/_init_db')
def initialize_database():
    try:
        from db.database import get_db
        db = get_db()
        
        # --- MONGODB INITIALIZATION ---
        # 1. Create Indexes
        db.users.create_index("email", unique=True)
        db.admins.create_index("email", unique=True)
        db.ngos.create_index("contact_email", unique=True)
        
        # 2. Create Default Admin if not exists
        if not db.admins.find_one({"email": "admin@donatewise.com"}):
            from werkzeug.security import generate_password_hash
            hashed = generate_password_hash('admin123')
            db.admins.insert_one({
                "name": "Admin", 
                "email": "admin@donatewise.com", 
                "password_hash": hashed, 
                "role": "admin"
            })
            
        return "✅ MongoDB initialized successfully (indexes created, admin user ensured)."

    except Exception as e:
        return f"❌ Initialization failed: {e}"

"""
@main.route('/_init_db_mysql')
def initialize_database_mysql():
    try:
        from db.database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100) UNIQUE, password_hash VARCHAR(255), role VARCHAR(20) DEFAULT 'donor')")
        
        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash('admin123')
        cur.execute('INSERT IGNORE INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)', ("Admin", "admin@donatewise.com", hashed, "admin"))
        
        cur.execute("CREATE TABLE IF NOT EXISTS donations (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, title VARCHAR(200), description TEXT, predicted_category VARCHAR(50), quantity VARCHAR(50), pickup_status VARCHAR(20) DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, location VARCHAR(255), image_filename VARCHAR(255), FOREIGN KEY (user_id) REFERENCES users(id))")
        
        cur.execute("CREATE TABLE IF NOT EXISTS donation_claims (id INT AUTO_INCREMENT PRIMARY KEY, donation_id INT, ngo_id INT, pickup_time DATETIME, status VARCHAR(20) DEFAULT 'claimed', FOREIGN KEY (donation_id) REFERENCES donations(id), FOREIGN KEY (ngo_id) REFERENCES users(id))")
        
        cur.execute("CREATE TABLE IF NOT EXISTS ngos (id INT PRIMARY KEY, org_name VARCHAR(200), location VARCHAR(255), license_no VARCHAR(50), status VARCHAR(20) DEFAULT 'pending', FOREIGN KEY (id) REFERENCES users(id))")

        conn.commit()
        cur.close()
        conn.close()
        return "✅ Local MySQL database initialized successfully."
    except Exception as e:
        return f"❌ Initialization failed: {e}"
"""

@main.route('/')
def index():
    return redirect(url_for('main.home'))

@main.route('/home')
def home():
    if session.get('role') != 'donor':
        flash("Please log in as donor to access home.")
        return redirect(url_for('auth.login'))
    
    # 📢 Fetch active NGO requirements for the 'Needs Board'
    active_needs = get_all_active_needs()
    impact_stats = get_impact_stats()
    top_donors = get_top_donors()
    map_data = get_recent_map_data()
    activity_feed = get_live_activity_feed(8)
    notifications = get_user_notifications(session['user_id'])

    return render_template('landing.html', 
                           active_needs=active_needs,
                           impact_stats=impact_stats,
                           top_donors=top_donors,
                           map_data=map_data,
                           activity_feed=activity_feed,
                           notifications=notifications,
                           notif_count=len(notifications))

@main.route('/needs')
def needs_board():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    active_needs = get_all_active_needs()
    return render_template('needs.html', active_needs=active_needs)

@main.route('/profile')
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    stats = get_donor_profile_stats(user_id)
    badges = get_donor_badges(stats)
    
    user_id = session['user_id']
    stats = get_donor_profile_stats(user_id)
    badges = get_donor_badges(stats)
    
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    from bson import ObjectId
    db = get_db()
    
    # Fetch recent history with NGO info
    recent_cursor = db.donations.aggregate([
        {"$match": {"user_id": user_id}},
        {"$sort": {"created_at": -1}},
        {"$limit": 5},
        {
            "$lookup": {
                "from": "ngos",
                "let": {"claimed_by_id": "$claimed_by"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$claimed_by_id"]}}}
                ],
                "as": "ngo_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "title": 1,
                "predicted_category": 1,
                "quantity": 1,
                "pickup_status": 1,
                "created_at": 1,
                "location": 1,
                "image_filename": 1,
                "ngo_name": {"$arrayElemAt": ["$ngo_info.org_name", 0]}
            }
        }
    ])
    recent = list(recent_cursor)

    # # Get recent history for the feed
    # conn = get_db_connection()
    # cur = conn.cursor(dictionary=True)
    # cur.execute("""
    #     SELECT d.id, d.title, d.predicted_category, d.quantity, 
    #            d.pickup_status, d.created_at, d.location, d.image_filename,
    #            n.org_name as ngo_name
    #     FROM donations d
    #     LEFT JOIN donation_claims dc ON d.id = dc.donation_id
    #     LEFT JOIN ngos n ON dc.ngo_id = n.id
    #     WHERE d.user_id = %s
    #     ORDER BY d.created_at DESC
    #     LIMIT 5
    # """, (user_id,))
    # recent = cur.fetchall()
    # cur.close()
    # conn.close()

    
    return render_template('profile.html',
                           user_name=session.get('name', 'Donor'),
                           stats=stats,
                           badges=badges,
                           recent=recent)

@main.route('/api/activity')
def api_activity():
    """Returns live activity feed as JSON for polling."""
    from flask import jsonify
    feed = get_live_activity_feed(10)
    for e in feed:
        if e.get('time'):
            e['time'] = str(e['time'])
    return jsonify(feed)

@main.route('/api/notifications')
def api_notifications():
    """Returns user notifications as JSON for polling."""
    from flask import jsonify
    if not session.get('user_id'):
        return jsonify([])
    notifs = get_user_notifications(session['user_id'])
    return jsonify({'count': len(notifs), 'items': notifs})

@main.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        flash("Admin access only.")
        return redirect(url_for('auth.admin_login'))

    stats = get_category_stats()
    donations = get_all_donations()
    
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    db = get_db()
    pending_ngos = list(db.ngos.find({"status": "Pending"}))
    for ngo in pending_ngos:
        ngo['id'] = str(ngo['_id'])

    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE TRIM(LOWER(status)) = 'pending'")
    pending_ngos = cur.fetchall()
    cur.close()
    conn.close()
    """

    for d in donations:
        d['pickup_recommended'] = False
        if d.get('pickup_required'):
            d['pickup_recommended'] = should_recommend_pickup(
                d['quantity'], d['predicted_category'], d['description']
            )
    return render_template('dashboard.html', donations=donations, stats=stats, pending_ngos=pending_ngos)

@main.route('/donate', methods=['GET', 'POST'])
def donate():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        quantity = request.form.get('quantity', '1')
        pickup_required = 'pickup_required' in request.form
        pickup_time = request.form.get('pickup_time') or None

        image_file = request.files.get('image')
        image_url = None
        visual_hint = ""
        
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            
            # ☁️ Attempt Cloudinary Upload (Recommended for Vercel)
            if CLOUDINARY_API_KEY:
                try:
                    upload_result = cloudinary.uploader.upload(image_file, folder="donatewise")
                    image_url = upload_result.get('secure_url')
                    print(f"☁️ Cloudinary upload successful: {image_url}")
                except Exception as e:
                    print(f"❌ Cloudinary upload failed: {e}")
            
            # 📂 Fallback to local storage (if Cloudinary fails or is not configured)
            if not image_url:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(save_path)
                image_url = filename # Storing just filename for local
            
            # 🔍 'Vision-Lite' Heuristic: Extract keywords from filename for better accuracy
            # This makes the AI feel much smarter when text descriptions are missing
            file_lower = filename.lower()
            hints = {
                'Food': ['food', 'veg', 'fruit', 'apple', 'bread', 'rice', 'meal', 'grocery'],
                'Clothes': ['shirt', 'pant', 'jean', 'jacket', 'cloth', 'wear', 'shoes'],
                'Electronics': ['mobile', 'phone', 'laptop', 'tv', 'fridge', 'appliances', 'gadget'],
                'Books': ['book', 'note', 'text', 'novel', 'study'],
                'Furniture': ['chair', 'table', 'sofa', 'bed', 'shelf', 'desk'],
                'Medical': ['med', 'tablet', 'health', 'surgical', 'mask'],
                'Toys': ['toy', 'doll', 'game', 'play', 'teddy']
            }
            for cat, keywords in hints.items():
                if any(k in file_lower for k in keywords):
                    visual_hint = f" This appears to be {cat} based on visual analysis."
                    break

        # If title is empty, use a generic placeholder for the DB
        if not title and image_url:
            title = "Image-based Donation"
        if not description and image_url:
            description = "No description provided."

        # Combine text and visual hints for the predictor
        prediction_text = f"{title} {description} {visual_hint}".strip()
        impact = predict_impact(prediction_text)
        
        pickup_recommended = should_recommend_pickup(quantity, impact['category'], description)

        session['donation_data'] = {
            'title': title,
            'description': description,
            'location': location,
            'quantity': quantity,
            'predicted_category': impact['category'],
            'ai_condition': impact['condition'],
            'ai_confidence': impact['confidence'],
            'image_filename': image_url,
            'pickup_required': pickup_required,
            'pickup_time': pickup_time,
            'pickup_status': 'Pending',
            'pickup_recommended': pickup_recommended
        }

        return redirect(url_for('main.result'))

    return render_template('donate.html')

@main.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    text = f"{data.get('title', '')} {data.get('description', '')}"
    prediction = predict_impact(text)
    return prediction

@main.route('/result', methods=['GET', 'POST'])
def result():
    data = session.get('donation_data')
    if request.method == 'POST' and data and session.get('user_id'):
        save_donation(
            user_id=session['user_id'],
            title=data['title'],
            description=data['description'],
            location=data['location'],
            quantity=data['quantity'],
            predicted_category=data['predicted_category'],
            image_filename=data.get('image_filename'),
            pickup_required=data.get('pickup_required'),
            pickup_time=data.get('pickup_time'),
            pickup_status=data.get('pickup_status')
        )
        flash("Donation confirmed successfully!")
        return redirect(url_for('main.dashboard'))
    return render_template('result.html', prediction=data.get('predicted_category'))

@main.route('/confirm', methods=['POST'])
def confirm():
    user_id = session.get('user_id')
    data = session.get('donation_data')
    manual_category = request.form.get('manual_category')

    if data and user_id:
        # If user chose a different category manually, use it
        final_category = manual_category if manual_category else data['predicted_category']
        
        save_donation(
            user_id=user_id,
            title=data['title'],
            description=data['description'],
            location=data['location'],
            quantity=data['quantity'],
            predicted_category=final_category,
            image_filename=data.get('image_filename'),
            pickup_required=data.get('pickup_required'),
            pickup_time=data.get('pickup_time'),
            pickup_status=data.get('pickup_status')
        )
        flash(f"Donation confirmed and categorized as {final_category}!")
        return redirect(url_for('main.home'))
    else:
        flash("Missing donation data or user session.")
        return redirect(url_for('main.donate'))

@main.route('/verify_pickup', methods=['POST'])
def verify_pickup():
    donation_id = request.form.get('donation_id')
    action = request.form.get('action')

    if donation_id and action:
        if action == "approve":
            update_pickup_status(donation_id, "Approved")
            flash(f"✅ Pickup approved for donation ID {donation_id}")
        elif action == "decline":
            update_pickup_status(donation_id, "Declined")
            flash(f"❌ Pickup declined for donation ID {donation_id}")
    else:
        flash("❌ Invalid request for pickup verification.")
    return redirect(url_for('main.dashboard'))

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    return render_template('feedback.html')

@main.route('/history')
def history():
    if not session.get('user_id'):
        flash("Please log in to view your history.")
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    db = get_db()
    
    # Fetch user donations with claim info if available
    history_cursor = db.donations.aggregate([
        {"$match": {"user_id": user_id}},
        {"$sort": {"created_at": -1}},
        {
            "$lookup": {
                "from": "ngos",
                "let": {"claimed_by_id": "$claimed_by"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$claimed_by_id"]}}}
                ],
                "as": "ngo_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "title": 1,
                "description": 1,
                "predicted_category": 1,
                "quantity": 1,
                "pickup_status": 1,
                "created_at": 1,
                "location": 1,
                "image_filename": 1,
                "claimed_by": 1,
                "pickup_required": 1,
                "pickup_time": 1,
                "ngo_name": {"$arrayElemAt": ["$ngo_info.org_name", 0]},
                "ngo_location": {"$arrayElemAt": ["$ngo_info.location", 0]}
            }
        }
    ])
    history_data = list(history_cursor)
    
    # conn = get_db_connection()
    # cur = conn.cursor(dictionary=True)
    # 
    # # Fetch user donations with claim info if available
    # query = """
    #     SELECT d.*, n.org_name as ngo_name, n.location as ngo_location, 
    #            dc.pickup_time as scheduled_time, 
    #            dc.status as claim_status, dc.pickup_notes
    #     FROM donations d
    #     LEFT JOIN donation_claims dc ON d.id = dc.donation_id
    #     LEFT JOIN ngos n ON dc.ngo_id = n.id
    #     WHERE d.user_id = %s
    #     ORDER BY d.created_at DESC
    # """
    # cur.execute(query, (user_id,))
    # history_data = cur.fetchall()

    
    # Calculate stats for the impact summary
    total_donations = len(history_data)
    claimed_count = sum(1 for d in history_data if d.get('claimed_by'))
    pending_count = total_donations - claimed_count

    # cur.close()
    # conn.close()
    
    return render_template('history.html', 
                           history=history_data, 
                           stats={
                               'total': total_donations, 
                               'claimed': claimed_count, 
                               'pending': pending_count
                           })

@main.route('/certificate/<string:donation_id>')
def view_certificate(donation_id):
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    
    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    from bson import ObjectId
    from bson.errors import InvalidId
    db = get_db()
    
    try:
        don_id_obj = ObjectId(donation_id)
    except InvalidId:
        flash("Invalid Certificate ID.")
        return redirect(url_for('main.history'))
    
    # Securely fetch only if it belongs to the user and is FULFILLED
    donation_cursor = db.donations.aggregate([
        {"$match": {"_id": don_id_obj, "user_id": str(session['user_id']), "pickup_status": "Fulfilled"}},
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id_str": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$user_id_str"]}}}
                ],
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "ngos",
                "let": {"claimed_by_id": "$claimed_by"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$claimed_by_id"]}}}
                ],
                "as": "ngo_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "donor_name": {"$arrayElemAt": ["$user_info.name", 0]},
                "ngo_name": {"$arrayElemAt": ["$ngo_info.org_name", 0]},
                "title": 1,
                "created_at": 1,
                "quantity": 1,
                "predicted_category": 1
            }
        }
    ])
    donation = next(donation_cursor, None)

    # # Securely fetch only if it belongs to the user and is FULFILLED
    # conn = get_db_connection()
    # cur = conn.cursor(dictionary=True)
    # cur.execute("""
    #     SELECT d.*, u.name as donor_name, n.org_name as ngo_name
    #     FROM donations d
    #     JOIN users u ON d.user_id = u.id
    #     LEFT JOIN donation_claims dc ON d.id = dc.donation_id
    #     LEFT JOIN ngos n ON dc.ngo_id = n.id
    #     WHERE d.id = %s AND d.user_id = %s AND d.pickup_status = 'Fulfilled'
    # """, (donation_id, session['user_id']))
    # donation = cur.fetchone()
    # cur.close()
    # conn.close()

    
    if not donation:
        flash("Certificate not available yet. Impact must be verified first!")
        return redirect(url_for('main.history'))
        
    if donation.get('created_at'):
        donation['created_at'] = str(donation['created_at'])
        
    return render_template('certificate.html', donation=donation)


# 🔔 Notify donor — keeps both in-app and email channels alive
def notify_donor(donation_id, pickup_time, ngo_name, event='claim'):
    donor = get_donor_by_donation_id(donation_id)
    print(f"📣 notify_donor() triggered. ID={donation_id} NGO={ngo_name} Event={event}")
    if not donor:
        print(f"❌ Error: No donor found for donation_id {donation_id}")
        return
    if not donor.get('email'):
        print(f"⚠️ Warning: Donor {donor.get('name')} has no email address. Skipping email.")
        return
    
    donation_title = donor.get('donation_title') or f'Donation #{donation_id}'
    to_email = donor['email']
    print(f"📬 Attempting to send '{event}' email to {to_email}...")
    
    if event == 'claim':
        send_claimed_notification(to_email, donor['name'], donation_title, ngo_name, pickup_time)
    elif event == 'dispatch':
        send_dispatched_notification(to_email, donor['name'], donation_title, ngo_name)
    elif event == 'fulfill':
        send_fulfilled_notification(to_email, donor['name'], donation_title, ngo_name)

# 🔷 NGO ROUTES

@main.route('/ngo/dashboard')
def ngo_dashboard():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))

    ngo = get_ngo_profile(session['ngo_id'])
    if not ngo:
        flash("NGO profile could not be loaded.")
        return redirect(url_for('main.ngo_profile'))

    stats = get_category_stats()
    unclaimed = get_unclaimed_donations()
    claimed = get_claimed_donations(session['ngo_id'])

    # 📍 Proximity Logic: Find donations near the NGO
    ngo_area = ngo['location'].split(',')[-1].strip().lower() # Assuming last part is Area/City
    
    for d in unclaimed + claimed:
        d['pickup_status'] = d.get('pickup_status') or 'Pending'
        d['pickup_recommended'] = should_recommend_pickup(
            d['quantity'], d['predicted_category'], d['description']
        )
        
        # Check if nearby
        d_loc = d['location'].lower()
        d['is_nearby'] = ngo_area in d_loc or d_loc in ngo_area

    return render_template('ngo_dashboard.html', 
                           stats=stats, 
                           unclaimed=unclaimed, 
                           claimed=claimed, 
                           ngo=ngo, 
                           ngo_area=ngo_area)


@main.route('/ngo/claim', methods=['POST'])
def claim_donation():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.ngo_login'))

    ngo = get_ngo_profile(session['ngo_id'])
    if ngo['status'] != 'Approved':
        flash("🚫 Only verified NGOs can claim donations. Please wait for admin approval.")
        return redirect(url_for('main.ngo_dashboard'))

    donation_id = request.form.get('donation_id')
    pickup_time = request.form.get('pickup_time')
    pickup_notes = request.form.get('pickup_notes')

    if not donation_id or not pickup_time:
        flash("⚠️ Pickup time is required to claim.")
        return redirect(url_for('main.ngo_dashboard'))

    # --- MONGODB IMPLEMENTATION ---
    mark_donation_claimed(donation_id, session['ngo_id'], pickup_time, pickup_notes)
    
    # conn = get_db_connection()
    # cur = conn.cursor()
    # # cur.execute("""
    # #     INSERT INTO donation_claims (donation_id, ngo_id, pickup_time, pickup_notes, status)
    # #     VALUES (%s, %s, %s, %s, %s)
    # # """, (donation_id, session['ngo_id'], pickup_time, pickup_notes, 'Scheduled'))
    # # 
    # # cur.execute("""
    # #     UPDATE donations SET claimed_by = %s WHERE id = %s
    # # """, (session['ngo_id'], donation_id))
    # # 
    # # conn.commit()
    # # cur.close()
    # # conn.close()


    ngo_name = ngo.get('org_name') or 'your NGO'
    notify_donor(donation_id, pickup_time, ngo_name)

    flash(Markup(
        f"✅ Claimed for pickup at <strong>{pickup_time}</strong>. " +
        f"<a href='{url_for('main.ngo_claimed')}' class='btn btn-sm btn-success ms-2'>View Claimed Donations</a>"
    ))
    return redirect(url_for('main.ngo_dashboard'))


@main.route('/ngo/claimed')
def ngo_claimed():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))
    claimed = get_claimed_donations(session['ngo_id'])
    return render_template('ngo_claimed.html', claimed=claimed)

@main.route('/ngo/fulfill', methods=['POST'])
def fulfill_donation_route():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))

    donation_id = request.form.get('donation_id')
    if donation_id:
        mark_donation_fulfilled(donation_id)
        ngo = get_ngo_profile(session['ngo_id'])
        ngo_name = ngo.get('org_name', 'NGO') if ngo else 'NGO'
        # 📧 Send fulfillment email + in-app notification updates automatically
        notify_donor(donation_id, None, ngo_name, event='fulfill')
        flash("🎉 Delivery confirmed! Donor has been notified and can now claim their Impact Certificate.")
    return redirect(url_for('main.ngo_claimed'))

@main.route('/ngo/dispatch', methods=['POST'])
def dispatch_donation_route():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))

    donation_id = request.form.get('donation_id')
    if donation_id:
        mark_donation_dispatched(donation_id)
        donor = get_donor_by_donation_id(donation_id)
        ngo = get_ngo_profile(session['ngo_id'])
        ngo_name = ngo.get('org_name', 'NGO') if ngo else 'NGO'
        # 📧 Email + in-app notification
        notify_donor(donation_id, None, ngo_name, event='dispatch')
        flash(f"🚚 Journey Started! {donor['name'] if donor else 'Donor'} will now see live tracking on their history page.")
    return redirect(url_for('main.ngo_claimed'))

@main.route('/ngo/profile')
def ngo_profile():
    if not session.get('ngo_id'):
        flash("🚫 Session expired. Please log in again.")
        return redirect(url_for('auth.login'))

    ngo_id = session['ngo_id']

    # --- MONGODB IMPLEMENTATION ---
    from db.database import get_db
    from bson import ObjectId
    db = get_db()
    ngo = db.ngos.find_one({"_id": ObjectId(ngo_id)})
    if ngo:
        ngo['id'] = str(ngo['_id'])

    """
    # ✅ Always fetch latest profile directly from DB
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ngos WHERE id = %s", (ngo_id,))
    ngo = cur.fetchone()
    cur.close()
    conn.close()
    """

    if not ngo:
        flash("⚠️ NGO profile not found.")
        return redirect(url_for('auth.login'))

    print(f"🧪 NGO Profile Loaded: {ngo['org_name']} - Status: {repr(ngo['status'])}")
    return render_template('ngo_profile.html', ngo=ngo)


@main.route('/ngo/needs', methods=['GET'])
def ngo_needs():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))
    needs = get_ngo_active_needs(session['ngo_id'])
    return render_template('ngo_needs.html', needs=needs)

@main.route('/ngo/post-need', methods=['POST'])
def post_ngo_need():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))
    
    ngo_id = session['ngo_id']
    category = request.form.get('category')
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    priority = request.form.get('priority')
    description = request.form.get('description')
    
    post_need(ngo_id, category, item_name, quantity, description, priority)
    flash("✅ Urgent requirement posted successfully!")
    return redirect(url_for('main.ngo_needs'))

@main.route('/ngo/delete-need/<string:need_id>', methods=['POST'])
def delete_ngo_need(need_id):
    if not session.get('ngo_id'):
        return redirect(url_for('auth.login'))
    
    delete_need(need_id, session['ngo_id'])
    flash("🗑️ Requirement removed.")
    return redirect(url_for('main.ngo_needs'))


@main.route('/ngo/register', methods=['GET', 'POST'])
def register_ngo_route():
    if request.method == 'POST':
        org_name = request.form.get('org_name')
        contact_email = request.form.get('contact_email')
        location = request.form.get('location')
        mission = request.form.get('mission')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # 🔒 Validate all required fields
        if not all([org_name, contact_email, location, mission, password, confirm]):
            flash("⚠️ Please fill out all fields.")
            return redirect(url_for('main.register_ngo_route'))

        if password != confirm:
            flash("❌ Passwords do not match.")
            return redirect(url_for('main.register_ngo_route'))

        hashed_password = generate_password_hash(password)

        try:
            # --- MONGODB IMPLEMENTATION ---
            register_ngo(org_name, contact_email, location, mission, hashed_password)
            flash("✅ NGO registration successful! Awaiting admin approval. Please log in.")
            return redirect(url_for('auth.ngo_login'))

            # conn = None
            # cur = None
            # conn = get_db_connection()
            # cur = conn.cursor()
            # cur.execute("""
            #     INSERT INTO ngos (org_name, contact_email, location, mission, password_hash, status)
            #     VALUES (%s, %s, %s, %s, %s, %s)
            # """, (org_name, contact_email, location, mission, hashed_password, 'Pending'))
            # conn.commit()
            # flash("✅ NGO registration successful! Awaiting admin approval. Please log in.")
            # return redirect(url_for('auth.ngo_login'))


        except Exception as e:
            print("❌ NGO registration failed:", e)
            flash("An error occurred during registration. Please try again.")

        finally:
            pass
            # if cur:
            #     cur.close()
            # if conn:
            #     conn.close()

    return render_template('ngo_register.html')
