from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Artwork
from app.forms import SignupForm, LoginForm, ArtworkForm
import os
import secret
import qrcode
from stegano import lsb
from PIL import Image
import io
import base64
from io import BytesIO

# Create a Blueprint for main routes
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/gallery')
def gallery():
    sort_by = request.args.get('sort', 'latest')

    if sort_by == 'latest':
        artworks = Artwork.query.order_by(Artwork.id.desc()).all()
    elif sort_by == 'oldest':
        artworks = Artwork.query.order_by(Artwork.id.asc()).all()
    elif sort_by == 'alphabetical':
        artworks = Artwork.query.order_by(Artwork.title.asc()).all()
    else:
        artworks = Artwork.query.order_by(Artwork.id.desc()).all()

    return render_template('gallery.html', artworks=artworks, sort_by=sort_by)


@main_routes.route('/artist/<username>')
def artist_profile(username):
    artist = User.query.filter_by(username=username).first_or_404()
    artworks = Artwork.query.filter_by(artist_id=artist.id).all()
    return render_template('artist_profile.html', artist=artist, artworks=artworks)

@main_routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_artwork():
    form = ArtworkForm()
    if form.validate_on_submit():
        # Save the uploaded image
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config['ARTWORKS_UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)

        # Generate QR code linking to the artist's profile
        artist_profile_url = url_for('main.artist_profile', username=current_user.username, _external=True)
        qr_image = generate_qr_code(artist_profile_url)

        # Embed QR code in the artwork image
        artwork_image = Image.open(image_path)
        secret_image = embed_qr_in_artwork(artwork_image, qr_image)
        secret_image.save(image_path)  # Overwrite the original image with the embedded QR code

        # Save artwork details to the database
        image_url = os.path.join('static', 'uploads', 'artworks', filename).replace("\\", "/")
        artwork = Artwork(
            title=form.title.data,
            description=form.description.data,
            image_url=image_url,
            artist_id=current_user.id
        )
        db.session.add(artwork)
        db.session.commit()

        flash('Artwork uploaded successfully!', 'success')
        return redirect(url_for('main.gallery'))
    return render_template('upload_artwork.html', form=form)

# View artwork one by one
@main_routes.route('/artwork/<int:artwork_id>')
def artwork_detail(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    return render_template('artwork_detail.html', artwork=artwork)

# Helper functions for QR code generation and embedding
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')
    return qr_img

def embed_qr_in_artwork(artwork_image, qr_image):
    # Convert QR image to bytes
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")
    qr_text = base64.b64encode(buffered.getvalue()).decode()  # Convert image to base64 string

    # Embed QR code as text using stegano
    secret_image = lsb.hide(artwork_image, qr_text)
    return secret_image

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