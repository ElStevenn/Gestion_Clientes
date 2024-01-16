#!/usr/bin/env python3 



from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.future import select
from . import models
from base64 import b64encode
import asyncio
from .database import AsyncSessionLocal, async_engine, AsyncEngine



async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as db:
        yield db


async def get_user(db: AsyncSession, username: str):
    """get user data by its name"""
    async with async_engine.connect() as conn:
        # Set a result, whitch will be delivred with buffered
        pre_result = await conn.execute(select(models.Authorized_users).where(models.Authorized_users.username == username))
    await async_engine.dispose()
   
    return pre_result.first()




async def main():


    """
    new_user = schemas.CreateUser(
        username="root",
        email="puercoespin",
        password="mierda69",
        role_="owner"
    )
    """
"""    async with AsyncSession(async_engine) as db:
        result = await check_session(db, 'root', 'mierda69')

        # print(result)
        

    # print(ecipher_text, salt, nonce, tag)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
"""