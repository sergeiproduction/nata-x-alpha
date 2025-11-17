from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.base import Base
from database.models.user_referral import UserReferral

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    telegram_id = Column(Integer, unique=True)
    inn = Column(String)
    register_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    invoices = relationship("Invoice", back_populates="user")

    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    referrals_made = relationship("UserReferral", foreign_keys=[UserReferral.user_id], back_populates="user")
    referrals_received = relationship("UserReferral", foreign_keys=[UserReferral.referrer_id], back_populates="referrer")
    user_notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")
    user_promocodes = relationship("UserPromocode", back_populates="user")
    user_checklist_items = relationship("UserChecklistItem", back_populates="user")
    user_subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")