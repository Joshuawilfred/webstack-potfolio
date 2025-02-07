import sqlite3
import random
from datetime import datetime

DB_PATH = "instance/art_gallery.db"

def populate_follows():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    user_ids = list(range(1, 50))  # Users 1 to 49

    follows = set()  # Avoid duplicates

    for follower in user_ids:
        followed_candidates = [u for u in user_ids if u != follower]  # Exclude self-follow
        followed_count = random.randint(3, 10)  # Each user follows 3-10 others

        for followed in random.sample(followed_candidates, followed_count):
            follows.add((follower, followed))

    # Insert into DB
    cursor.executemany("""
        INSERT INTO follows (follower_id, followed_id, created_at) VALUES (?, ?, ?)
    """, [(f[0], f[1], datetime.utcnow()) for f in follows])

    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(follows)} follow relationships.")

populate_follows()
