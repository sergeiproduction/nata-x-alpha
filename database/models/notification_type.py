from sqlalchemy import Column, Integer, String, Boolean, SmallInteger
from sqlalchemy.orm import relationship
from database.base import Base

class NotificationType(Base):
    __tablename__ = "notification_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    default_enabled = Column(Boolean, default=True, nullable=False)
    advance_days = Column(SmallInteger, default=1, nullable=False)

    user_notifications = relationship("UserNotification", back_populates="notification_type", cascade="all, delete-orphan")