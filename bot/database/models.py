from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    username = Column(String)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    messages_today = Column(Integer, default=0)
    last_message_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime)
    
    user = relationship("User", back_populates="subscription") 