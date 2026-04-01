import time
from aiogram import BaseMiddleware

class Throttle(BaseMiddleware):
    def __init__(self, rate=2):
        self.rate = rate
        self.users = {}

    async def __call__(self, handler, event, data):
        user = event.from_user.id

        now = time.time()
        last = self.users.get(user, 0)

        if now - last < self.rate:
            return

        self.users[user] = now
        return await handler(event, data)
