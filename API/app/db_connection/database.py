#!/usr/bin/env python3
"""
    Database connection
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
import os
import asyncio
from sqlalchemy import MetaData

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:mierda69@185.254.206.129:5432/paudatabase"
# Connection postgresql://<user>:<password>@<host>:<port>/<database_name>
# Port: 5432

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=True, 
    autoflush=False
)

Base = declarative_base()


async def get_all_table_names():
    """Test to see if the connection was successfully"""
    async with async_engine.connect() as conn:
        meta = MetaData()
        await conn.run_sync(meta.reflect)
        return list(meta.tables.keys())
    
if __name__ == "__main__":
    result = asyncio.run(get_all_table_names())
    print(result)