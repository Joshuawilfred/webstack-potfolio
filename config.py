import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///art_gallery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    ARTWORKS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'artworks')

    # Ensure upload directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ARTWORKS_UPLOAD_FOLDER, exist_ok=True)
