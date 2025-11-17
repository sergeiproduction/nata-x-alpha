from sqlalchemy import Column, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class UserChecklistItem(Base):
    __tablename__ = "user_checklist_items"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, nullable=False)
    item_id = Column(Integer, ForeignKey("checklist_items.id"), primary_key=True, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Связи
    user = relationship("User", back_populates="user_checklist_items")
    item = relationship("ChecklistItem", back_populates="user_items")