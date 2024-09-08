import asyncio
from database.db_helper import db_helper

async def main():
    await db_helper.init_db()


asyncio.run(main())