# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query = Column(String(255), nullable=False)
    search_time = Column(DateTime, default=datetime.utcnow)
    results = Column(JSON)  # Assuming JSON is required for results

    user = relationship("User", back_populates="search_histories")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    price = Column(String(50))
    link = Column(String(255))
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(Float)  # Add rating attribute
