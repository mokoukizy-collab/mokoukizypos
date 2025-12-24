from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String, default="open", index=True)
    printed = Column(Integer, default=1)
    note = Column(Text, default="")
    subtotal = Column(Integer, default=0)
    discount = Column(Integer, default=0)
    allowance = Column(Integer, default=0)
    total = Column(Integer, default=0)
    count = Column(Integer, default=0)
    table_no = Column(Integer, nullable=True)
    dine_type = Column(String, default="外帶")
    started_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    name = Column(String)
    unit_price = Column(Integer)
    quantity = Column(Integer)
    details = Column(Text, default="")
    order = relationship("Order", back_populates="items")
