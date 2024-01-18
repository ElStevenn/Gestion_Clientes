import sys
print(sys.path)

from ..security import create_user
import asyncio
from .crud import get_db
from .schemas import CreateUser
from .database import AsyncSession, async_engine

async def create_users(users, db):
    for user_data in users:
        user = CreateUser(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role_']
        )

        await create_user(db, user)

async def main():
    users = [

        {
            "username":"anna_cramling",
            "email":"annacramling@gmail.com",
            "role_":"user",
            "password":"hola123"
        }
    ]

    async with AsyncSession(async_engine) as db:
        await create_users(users, db)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
