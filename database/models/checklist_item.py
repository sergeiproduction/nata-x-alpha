from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    content = Column(String, nullable=False)


    checklist = relationship("Checklist", back_populates="checklist_items")
    user_items = relationship("UserChecklistItem", back_populates="item", cascade="all, delete-orphan")