import os
from PIL import Image
from stegano import lsb
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from pyzbar.pyzbar import decode

def embed_qr_code(image_path, artist_url):
    """Embed artist URL in image as QR code"""
    try:
        # Convert image to PNG (ensuring lossless storage)
        artwork_img = Image.open(image_path).convert("RGB")
        png_path = image_path.rsplit(".", 1)[0] + ".png"
        artwork_img.save(png_path, format="PNG")

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(artist_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')

        # Convert QR to base64
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_text = base64.b64encode(buffered.getvalue()).decode()

        # Embed in PNG image
        secret_img = lsb.hide(png_path, qr_text)
        output_path = os.path.join('app', 'static', 'uploads', 'artworks', f"encoded_{os.path.basename(png_path)}").replace("\\", "/")
        secret_img.save(output_path)

        return output_path

    except Exception as e:
        raise Exception(f"Error embedding QR code: {str(e)}")

def scan_qr_code(image_path):
    """Scan image for embedded QR code"""
    try:
        # Open the artwork image and convert to RGB if necessary
        artwork_img = Image.open(image_path)
        if artwork_img.mode != 'RGB':
            artwork_img = artwork_img.convert('RGB')

        # Extract hidden data
        hidden_data = lsb.reveal(artwork_img)

        if hidden_data:
            # Convert base64 to QR
            qr_bytes = base64.b64decode(hidden_data)
            qr_img = Image.open(BytesIO(qr_bytes))
            qr_data = decode(qr_img)

            # Decode QR
            if qr_data:
                artist_url = qr_data[0].data.decode()
                return artist_url

        raise Exception("No valid QR code found")

    except Exception as e:
        raise Exception(f"Error scanning QR code: {str(e)}")