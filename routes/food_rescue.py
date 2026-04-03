from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.food_rescue_model import post_food_rescue, get_active_rescues, get_rescues_by_ngo, claim_food_rescue, mark_food_picked_up
from models.ngo_models import get_ngo_profile
from markupsafe import Markup
from datetime import datetime

food_rescue_bp = Blueprint('food_rescue', __name__, url_prefix='/food-rescue')

@food_rescue_bp.route('/')
def landing():
    # Public mega food rescue landing page
    active_rescues = get_active_rescues()
    # sum of persons
    total_meals_available = sum(r['quantity_persons'] for r in active_rescues if not r['is_expired'])
    
    return render_template('food_rescue.html', 
                           active_rescues=active_rescues, 
                           total_meals_available=total_meals_available)

@food_rescue_bp.route('/submit', methods=['GET', 'POST'])
def submit_rescue():
    if not session.get('user_id'):
        flash("You must be logged in as a Donor to access Zero-Waste Mega Rescue.")
        return redirect(url_for('auth.login'))

    if session.get('role') != 'donor':
        flash("Only donors can submit food rescue requests.")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        event_type = request.form.get('event_type')
        food_type = request.form.get('food_type')
        quantity_persons = request.form.get('quantity_persons')
        address = request.form.get('address')
        contact_number = request.form.get('contact_number')
        best_before_hours = request.form.get('best_before_hours')
        pledge_accepted = request.form.get('pledge_accepted') == 'on'
        
        if not pledge_accepted:
            flash("❌ You must accept the pledge to guarantee food safety.")
            return redirect(url_for('food_rescue.submit_rescue'))
            
        post_food_rescue(
            donor_id=session['user_id'],
            event_type=event_type,
            food_type=food_type,
            quantity_persons=quantity_persons,
            address=address,
            contact_number=contact_number,
            best_before_hours=best_before_hours,
            pledge_accepted=pledge_accepted
        )
        
        flash("🚨 URGENT: Your bulk food rescue request is live! NGOs are being notified.", "success")
        return redirect(url_for('food_rescue.landing'))

    return render_template('food_rescue_submit.html')

@food_rescue_bp.route('/live-radar')
def live_radar():
    if not session.get('ngo_id'):
        flash("Access restricted. Only verified NGOs can view the active food radar.")
        return redirect(url_for('auth.ngo_login'))
        
    ngo = get_ngo_profile(session['ngo_id'])
    if ngo['status'] != 'Approved':
        flash("🚫 Only verified NGOs can claim bulk food rescue.")
        return redirect(url_for('main.ngo_dashboard'))

    active_rescues = get_active_rescues()
    my_claims = get_rescues_by_ngo(session['ngo_id'])

    return render_template('food_rescue_board.html', 
                           active_rescues=active_rescues,
                           my_claims=my_claims,
                           ngo=ngo)

@food_rescue_bp.route('/claim', methods=['POST'])
def claim_rescue():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.ngo_login'))
        
    ngo = get_ngo_profile(session['ngo_id'])
    if ngo['status'] != 'Approved':
        return redirect(url_for('main.ngo_dashboard'))

    rescue_id = request.form.get('rescue_id')
    eta_minutes = request.form.get('eta_minutes')

    if rescue_id and eta_minutes:
        claim_food_rescue(rescue_id, session['ngo_id'], int(eta_minutes))
        flash(Markup("✅ Highly coordinated pickup accepted! Please reach the destination within the ETA."))
    return redirect(url_for('food_rescue.live_radar'))

@food_rescue_bp.route('/picked-up', methods=['POST'])
def picked_up_rescue():
    if not session.get('ngo_id'):
        return redirect(url_for('auth.ngo_login'))

    rescue_id = request.form.get('rescue_id')
    if rescue_id:
        mark_food_picked_up(rescue_id)
        flash("🎉 Fantastic! The mega event food has been successfully rescued!")
        
    return redirect(url_for('food_rescue.live_radar'))
