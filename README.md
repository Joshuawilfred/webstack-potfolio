# Art Gallery Web Application

## Overview

This is a web application that allows artists to upload, share, and manage their artworks while providing users with a platform to discover and interact with art through unique features like embedded QR codes.

## Features

- **For Artists**:
  - Upload artworks with embedded metadata
  - Create personalized profiles with bio and gallery
  - Generate shareable QR codes hidden within images

- **For Users**:
  - Browse and discover artworks
  - Follow artists
  - View detailed artwork pages
  - Scan embedded QR codes for artist information

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Joshuawilfred/webstack-potfolio.git
   cd webstack-potfolio
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup and Seeding (Optional)

To populate the database with initial data: Download the [image assets](https://drive.google.com/drive/folders/1kwspMHvuyZdLkL4KMU_-xghEOWY1mJym?usp=drive_link) here and save it in `feed/assets`

1. Run user creation script:
   ```bash
   python feed/a_names.py
   ```

2. Create follow relationships:
   ```bash
   python feed/b_follows.py
   ```

3. Add artwork data:
   ```bash
   cat feed/c_data.py >> feed/c_artwork.py
   ```
   ```bash
   python feed/c_artwork.py
   ```

## Running the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Configuration

- By default, the app runs on port 5000. To change the port:
    1. Modify the `run.py` file:
        ```python
        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5001)  # Change port here
        ```
    2. Update the `artist_profile_url` in `feed/c_artwork.py` if you use the seeding scripts:
        ```python
        artist_profile_url = f"http://localhost:5001/artist/{artist_username}"
        ```
## CLI Tool:
  - **Embed QR Code**:
    ```bash
    python app/cli.py embed path/to/image.png "http://example.com/artist/username"
    ```
  - **Scan QR Code**:
    ```bash
    python app/cli.py scan  path/to/encoded-image.png
    ```

## License

MIT License

## Author

Joshua Wilfred
GitHub: [github.com/Joshuawilfred](https://github.com/Joshuawilfred)