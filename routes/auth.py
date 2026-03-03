from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models.user_model import get_user_by_email, register_user
from models.ngo_models import get_ngo_by_email
from models.admin_model import get_admin_by_email  # ✅ Use actual admin lookup

auth = Blueprint('auth', __name__)

# 📝 Donor Registration
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        register_user(name, email, hashed_password)
        flash('Account created! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

# 👤 Donor Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = 'donor'
            flash('Welcome back!')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid donor credentials.')
            return redirect(url_for('auth.login'))
    return render_template('donor_login.html')

# 🏢 NGO Login
@auth.route('/ngo/login', methods=['GET', 'POST'])
def ngo_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        ngo = get_ngo_by_email(email)

        if ngo and check_password_hash(ngo['password_hash'], password):
            session.clear()
            session['ngo_id'] = ngo['id']
            session['ngo_name'] = ngo['org_name']
            session['role'] = 'ngo'
            flash('NGO logged in successfully.')
            return redirect(url_for('main.ngo_dashboard'))
        else:
            flash('Invalid NGO credentials.')
            return redirect(url_for('auth.ngo_login'))
    return render_template('ngo_login.html')

# 🔐 Admin Login
@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = get_admin_by_email(email)

        if admin and check_password_hash(admin['password_hash'], password):
            session.clear()
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            session['role'] = 'admin'
            flash('Admin access granted.')
            return redirect(url_for('main.dashboard'))  # optional: replace with admin-specific view
        else:
            flash('Invalid admin credentials.')
            return redirect(url_for('auth.admin_login'))
    return render_template('admin_login.html')

# 🚪 Logout
@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
