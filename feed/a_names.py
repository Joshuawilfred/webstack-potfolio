import sqlite3
import random
from werkzeug.security import generate_password_hash

db_path = "instance/art_gallery.db"

users = [
    "Boston Public Library", "MCGill Library", "Brimingham", "Boston Public Library", "Andres Gomez",
    "The New York Library", "Europeana", "Jennifer Latuperisa", "Museums Victoria", "zhengtao Tang"
]

additional_names = [
    "Aisha Khan", "Dante Rossi", "Hiroshi Tanaka", "Fatima Al-Farsi", "Liam O'Connor",
    "Sophia Müller", "Chen Wei", "Isabella Fernández", "Raj Patel", "Elena Petrova",
    "Omar Abdallah", "Nguyen Minh", "Mateo Silva", "Amara Okafor", "Yuki Nakamura",
    "Giovanni Romano", "Adele Dupont", "Ethan Wright", "Selena Park", "Mikhail Ivanov",
    "Gabriela Costa", "David Stein", "Ananya Sharma", "Sven Lindberg", "Leila Haddad",
    "Lucas Moreau", "Carlos Mendes", "Yasmin Said", "Mohammed Reza", "Hannah Becker",
    "Zain Malik", "Camila Rojas", "Tariq Khan", "Simone Ricci", "Amina Yusuf",
    "Oliver Smith", "Nia Roberts", "Wei Zhang", "Fatou Diop", "Joshua Wilfred"
]

bios = [
    "Passionate art collector since 2010", "Digital art curator", "Photography enthusiast",
    "Abstract art specialist", "Contemporary art lover", "Renaissance art scholar",
    "Street art photographer", "Art history professor", "Museum curator", "Sculptor",
    "Visual artist", "Art restoration expert", "Gallery owner", "Art critic",
    "Digital illustrator", "Traditional painter", "Art educator", "Multimedia artist",
    "Art historian", "Performance artist"
]

all_users = list(set(users + additional_names))[:50]

def generate_email(name):
    if "Library" in name:
        return name.split()[0].lower() + "@gmail.com"
    return name.lower().replace(" ", "") + "@gmail.com"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        bio TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

for user in all_users:
    email = generate_email(user)
    password = generate_password_hash("Test@123", method='pbkdf2:sha256')
    bio = random.choice(bios)
    try:
        cursor.execute("INSERT INTO user (username, email, password, bio) VALUES (?, ?, ?, ?)", 
                      (user, email, password, bio))
    except sqlite3.IntegrityError:
        print(f"Skipping duplicate user: {user}")

conn.commit()
conn.close()

print("✅ Users populated successfully!")