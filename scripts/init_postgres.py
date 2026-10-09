import asyncio
import asyncpg

async def init_db():
    conn = await asyncpg.connect("postgresql://postgres@localhost:5432/postgres")
    try:
        await conn.execute("CREATE ROLE safescroll WITH LOGIN PASSWORD 'safescroll' SUPERUSER;")
        print("Role safescroll created.")
    except Exception as e:
        print("Role:", e)

    try:
        await conn.execute("CREATE DATABASE safescroll OWNER safescroll;")
        print("Database safescroll created.")
    except Exception as e:
        print("Database:", e)

    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())
