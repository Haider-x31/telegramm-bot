import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = list(map(int, os.getenv("ADMINS", "").split(",")))

VIP_POINTS = int(os.getenv("VIP_POINTS", 25))

REDIS_URL = os.getenv("REDIS_URL")
