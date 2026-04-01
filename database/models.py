from database.db import connect

async def init():
    db = await connect()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        points INTEGER DEFAULT 0,
        referrals INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0,
        is_vip INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        url TEXT PRIMARY KEY,
        file_id TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel TEXT
    )
    """)

    await db.commit()
