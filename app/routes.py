# routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Artwork
from app.forms import SignupForm, LoginForm, ArtworkForm
import os
import secrets
from PIL import Image
from io import BytesIO
from datetime import datetime

# Import QR code functions
from .my_qrcode import embed_qr_code, scan_qr_code

# Create a Blueprint for main routes
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/gallery')
@login_required
def gallery():
    filter_by = request.args.get('filter', 'foryou')  # Default to 'foryou'
    sort_by = request.args.get('sort', 'latest')  # Default sorting

    if filter_by == 'following':
        followed_ids = [f.followed_id for f in current_user.following]  # Get followed artist IDs
        artworks = Artwork.query.filter(Artwork.artist_id.in_(followed_ids))
    else:
        artworks = Artwork.query  # Default: show all artworks

    # Apply sorting
    if sort_by == 'oldest':
        artworks = artworks.order_by(Artwork.created_at.asc())
    elif sort_by == 'alphabetical':
        artworks = artworks.order_by(Artwork.title.asc())
    else:
        artworks = artworks.order_by(Artwork.created_at.desc())

    return render_template('gallery.html', artworks=artworks, sort_by=sort_by, filter_by=filter_by)

@main_routes.route('/artist/<username>')
def artist_profile(username):
    artist = User.query.filter_by(username=username).first_or_404()
    artworks = Artwork.query.filter_by(artist_id=artist.id).all()
    return render_template('artist_profile.html', artist=artist, artworks=artworks)

@main_routes.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    bio = request.form.get('bio')
    current_user.bio = bio
    db.session.commit()
    return redirect(url_for('main.artist_profile', username=current_user.username))

@main_routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_artwork():
    form = ArtworkForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config['ARTWORKS_UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)

        # Generate metadata & QR
        artist_profile_url = url_for('main.artist_profile', username=current_user.username, _external=True)
        output_path = embed_qr_code(image_path, artist_profile_url, current_user.username, form.title.data)

        # Save to DB
        artwork = Artwork(
            title=form.title.data,
            description=form.description.data,
            image_url=output_path,
            artist_id=current_user.id
        )
        db.session.add(artwork)
        db.session.commit()

        flash('Artwork uploaded successfully!', 'success')
        return redirect(url_for('main.gallery'))

    return render_template('upload_artwork.html', form=form)

@main_routes.route('/scan_qr', methods=['POST'])
def scan_qr():
    """Scan an artwork for embedded metadata"""
    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"success": False, "message": "No image URL provided."})

    image_path = os.path.join(current_app.root_path, 'static', image_url.split('static/')[-1])

    try:
        metadata = scan_qr_code(image_path)
        return jsonify({"success": True, "metadata": metadata})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Error: {str(e)}"})


@main_routes.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    return render_template('artwork_detail.html', artwork=artwork)

# Create a Blueprint for authentication routes
auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Hash the password before saving the user
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Create a new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password  # Store the hashed password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            flash('Email not found. Please sign up.', 'warning')
            return redirect(url_for('auth.signup'))

        if not check_password_hash(user.password, form.password.data):
            flash('Incorrect password. Try again.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form)

@auth_routes.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No account found with this email.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Generate a random token :)
        token = secrets.token_hex(16)
        
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        print(f'Password reset link (for demo): {reset_link}')  # Simulating email

        flash('If this email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@auth_routes.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        print(f'Password reset successful for token: {token}')
        flash('Password reset successful! Try logging in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

# Create a Blueprint for follow-related routes
follow_routes = Blueprint('follow', __name__)

@follow_routes.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if current_user.is_following(user_to_follow):
        flash('You are already following this user.', 'info')
    else:
        current_user.follow(user_to_follow)
        db.session.commit()
        flash(f'You are now following {user_to_follow.username}.', 'success')
    return redirect(request.referrer or url_for('main.index'))

@follow_routes.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.get_or_404(user_id)
    if not current_user.is_following(user_to_unfollow):
        flash('You are not following this user.', 'info')
    else:
        current_user.unfollow(user_to_unfollow)
        db.session.commit()
        flash(f'You have unfollowed {user_to_unfollow.username}.', 'success')
    return redirect(request.referrer or url_for('main.index'))