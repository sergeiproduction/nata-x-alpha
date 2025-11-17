from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database.base import Base

class UserReferral(Base):
    __tablename__ = "user_referrals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("user_id != referrer_id", name="check_user_not_referrer"),
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="referrals_made")
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_received")