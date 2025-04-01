import asyncio
from app.db import connect_to_mongo, is_connected


async def test_db_connection():
    await connect_to_mongo()  # Ensure connection is established
    connected = await is_connected()
    print("Database connected:", connected)


asyncio.run(test_db_connection())
