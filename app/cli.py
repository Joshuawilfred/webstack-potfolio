import click
import os
from PIL import Image
from stegano import lsb
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from pyzbar.pyzbar import decode

@click.group()
def cli():
    """Art Gallery QR Code CLI Tool"""
    pass

@cli.command()
@click.argument('image_path')
@click.argument('artist_url')
def embed(image_path, artist_url):
    """Embed artist URL in image as QR code"""
    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(artist_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        
        # Convert QR to base64
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_text = base64.b64encode(buffered.getvalue()).decode()
        
        # Open the artwork image and convert to RGB if necessary
        artwork_img = Image.open(image_path)
        if artwork_img.mode != 'RGB':
            artwork_img = artwork_img.convert('RGB')
        
        # Embed in artwork
        secret_img = lsb.hide(artwork_img, qr_text)
        output_path = f"encoded_{os.path.basename(image_path)}"
        secret_img.save(output_path)
        
        click.echo(f"✓ QR Code embedded successfully: {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('image_path')
def scan(image_path):
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
                click.echo("✓ Verification successful!")
                click.echo(f"Artist URL: {artist_url}")
                click.echo(f"Scanned on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                return
                
        click.echo("No valid QR code found", err=True)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()