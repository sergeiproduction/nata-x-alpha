from sqlalchemy import Column, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class UserNotification(Base):
    __tablename__ = "user_notifications"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, nullable=False)
    notification_type_id = Column(Integer, ForeignKey("notification_types.id"), primary_key=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="user_notifications")
    notification_type = relationship("NotificationType", back_populates="user_notifications")