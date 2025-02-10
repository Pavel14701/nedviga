import sqlalchemy as sa
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column 

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, index=True)
    firstname: Mapped[str] = mapped_column(sa.String(100), nullable=True)
    lastname: Mapped[str] = mapped_column(sa.String(100), nullable=True)
    username: Mapped[str] = mapped_column(sa.String(length=255), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(sa.String(length=30), unique=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(length=255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(length=255))
    salt: Mapped[str] = mapped_column(sa.String(length=16))
    is_active: Mapped[bool] = mapped_column(sa.Boolean)