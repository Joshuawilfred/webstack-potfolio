import json
import os
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image
from stegano import lsb
import qrcode
from pyzbar.pyzbar import decode

def embed_qr_code(image_path, artist_url, artist_name, artwork_title):
    """Embed QR code & metadata inside image"""
    try:
        # Ensure source image exists
        if not os.path.exists(image_path):
            raise Exception(f"Source image not found: {image_path}")

        # Convert image to PNG (lossless)
        artwork_img = Image.open(image_path).convert("RGB")
        png_path = image_path.rsplit(".", 1)[0] + ".png"
        artwork_img.save(png_path, format="PNG")

        # Generate QR code (profile link)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(artist_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Convert QR to base64
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Create metadata JSON
        metadata = {
            "artist_url": artist_url,
            "artist_name": artist_name,
            "artwork_title": artwork_title,
            "date_uploaded": datetime.utcnow().isoformat(),
            "qr_base64": qr_base64,  # Include QR as fallback
        }
        metadata_str = json.dumps(metadata)

        # Ensure output directory exists
        output_dir = os.path.join('app', 'static', 'uploads', 'artworks')
        os.makedirs(output_dir, exist_ok=True)

        # Hide metadata in image
        output_path = os.path.join(output_dir, f"encoded_{os.path.basename(png_path)}").replace("\\", "/")
        secret_img = lsb.hide(png_path, metadata_str)
        secret_img.save(output_path)

        # Confirm file was saved
        if not os.path.exists(output_path):
            raise Exception(f"Failed to save encoded image: {output_path}")

        print(f"✅ Encoded image saved at {output_path}")
        return output_path

    except Exception as e:
        raise Exception(f"Error embedding metadata: {str(e)}")

def scan_qr_code(image_path):
    """Extract metadata from image"""
    try:
        artwork_img = Image.open(image_path).convert("RGB")
        hidden_data = lsb.reveal(artwork_img)

        if hidden_data:
            metadata = json.loads(hidden_data)
            return metadata

        raise Exception("No valid metadata found")

    except Exception as e:
        raise Exception(f"Error scanning metadata: {str(e)}")
