import os
import sys
import sqlite3
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.my_qrcode import embed_qr_code
from app.models import User

# Database Path
DB_PATH = "instance/art_gallery.db"

# Artwork Upload Folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads', 'artworks')

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_artist_id(email):
    """Fetch artist ID from the database using email."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
    artist = cursor.fetchone()
    conn.close()
    return artist[0] if artist else None

def get_artist_username(artist_id):
    """Fetch artist username from the database using ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM user WHERE id = ?", (artist_id,))
    artist = cursor.fetchone()
    conn.close()
    return artist[0] if artist else None

def insert_artwork_with_qr(image_filename, title, description, artist_email):
    """Embed QR code, save image, and insert artwork into DB."""
    
    artist_id = get_artist_id(artist_email)
    if not artist_id:
        print(f"❌ Artist with email {artist_email} not found.")
        return
    
    # Paths
    image_path = os.path.join("feed/assets", image_filename)  # Original location / source image
    saved_path = os.path.join(UPLOAD_FOLDER, image_filename)  # Save location

    # Ensure source image exists
    if not os.path.exists(image_path):
        print(f"❌ Source image missing: {image_path}")
        return
    
    # Generate Artist Profile URL
    artist_username = get_artist_username(artist_id)
    artist_profile_url = f"http://localhost:5000/artist/{artist_username}"

    # Embed QR Code & Save Image
    try:
        encoded_image_path = embed_qr_code(image_path, artist_profile_url, artist_username, title)
        
        # Ensure encoded image was created
        if not encoded_image_path or not os.path.exists(encoded_image_path):
            print(f"❌ Failed to generate encoded image for {image_filename}")
            return
        
    except Exception as e:
        print(f"❌ Error embedding QR for {image_filename}: {e}")
        return

    # Insert into Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO artwork (title, description, image_url, created_at, artist_id)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, encoded_image_path, datetime.utcnow(), artist_id))
    
    conn.commit()
    conn.close()
    print(f"✅ Inserted {title} by {artist_email}")

# Paste the data from c_data here

