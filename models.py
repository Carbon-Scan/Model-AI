from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    struk = relationship("Struk", back_populates="user")


class Struk(Base):
    __tablename__ = "struk"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_emisi = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="struk")
    produk = relationship("Produk", back_populates="struk")


class Produk(Base):
    __tablename__ = "produk"

    id = Column(Integer, primary_key=True, index=True)
    struk_id = Column(Integer, ForeignKey("struk.id"))

    nama = Column(String(150), nullable=False)
    kategori = Column(String(100))
    berat_kg = Column(Float, default=0)
    karbon = Column(Float, default=0)
    karbon_factor = Column(Float, default=0)
    confidence = Column(Float, default=0)

    struk = relationship("Struk", back_populates="produk")
