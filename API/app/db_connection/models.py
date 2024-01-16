from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BINARY, Float, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid, requests
from sqlalchemy.orm import configure_mappers
configure_mappers()

from .database import Base

class Authorized_users(Base):
    __tablename__ = "authorized_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    ecipher_text = Column(BINARY, nullable=False)
    role_ = Column(String(10), nullable=False, default='user')
    salt = Column(BINARY, nullable=False)
    nonce = Column(BINARY, nullable=False)
    tag = Column(BINARY, nullable=False)

    def __repr__(self) -> dict:
        return dict(f"[{str(self.id)}, {self.username}, {self.email}, {self.role_}]")