from enum import Enum

from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column, 
    relationship
)
import sqlalchemy as sa


class Base(DeclarativeBase):
    pass


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class Chat(Base):
    __tablename__ = "chats"
    uuid: Mapped[str] = mapped_column(sa.UUID, primary_key=True, index=True)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime, default=sa.func.now())
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    uuid: Mapped[str] = mapped_column(sa.UUID, primary_key=True, index=True)
    chat_uuid: Mapped[str] = mapped_column(sa.UUID, sa.ForeignKey("chats.uuid"), nullable=False)
    sender_type: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    sender_uuid: Mapped[str] = mapped_column(sa.UUID, nullable=False)
    recipient_type: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    recipient_uuid: Mapped[str] = mapped_column(sa.UUID, nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)
    timestamp: Mapped[sa.DateTime] = mapped_column(sa.DateTime, default=sa.func.now())
    is_edited: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    edited_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime, default=None)
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")


class User(Base):
    __tablename__ = "users"
    uuid: Mapped[str] = mapped_column(sa.UUID, primary_key=True, index=True)
    firstname: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    username: Mapped[str] = mapped_column(sa.String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(sa.String(30), unique=True, index=True, nullable=True)
    password: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    role: Mapped[Role] = mapped_column(sa.Boolean, nullable=False, default=Role.USER)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime, default=sa.func.now())