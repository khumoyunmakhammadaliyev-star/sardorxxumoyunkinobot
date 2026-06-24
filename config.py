import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip()
]

CHANNEL_ID = os.getenv("CHANNEL_ID", "")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "")

DATABASE_URL = os.getenv("DATABASE_URL", "")

THROTTLE_RATE = float(os.getenv("THROTTLE_RATE", "1.5"))