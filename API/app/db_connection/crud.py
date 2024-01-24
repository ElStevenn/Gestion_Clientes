#!/usr/bin/env python3 

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.future import select
from sqlalchemy import and_
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


async def vadilate_user_credentials(username: str, role:str, id_:str): # End this please!
    """Vadilate user credentials by its user, role and id"""
    async with async_engine.connect() as conn:
        # Check the result
        try:
            result = await conn.execute(select(models.Authorized_users).where(and_(
                                    models.Authorized_users.username == username, 
                                    models.Authorized_users.role_ == role,
                                    models.Authorized_users.id == id_
                                    )))

            await async_engine.dispose()
            user_data = result.first()
            return user_data
        except TypeError:
            return None


async def main():
    id_ = "9c67e4b0-2821-417c-8cc4-62692d2a84b1"
    username = "root"
    role = "owner"

    result = await vadilate_user_credentials(username, role, id_)
    print(result)

if __name__ == "__main__":
   asyncio.run(main())