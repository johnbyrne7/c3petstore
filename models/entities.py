import datetime
from typing import TypedDict

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(DeclarativeBase):
    pass


class OrderPet(Base):
    __tablename__ = "order_pet"
    __table_args__ = (
        (UniqueConstraint("order_id", "pet_id", name="idx_order_pet_unique")),
        {
            "comment": "Junction table for many-to-many relationship between Order and Pet"
        },
    )
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id", ondelete="CASCADE"))
    pet_id = Column(Integer, ForeignKey("pet.id", ondelete="CASCADE"))
    quantity = Column(Integer, default="1")


class Pet(Base):
    __tablename__ = "pet"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(String, default="available")


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    ship_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=7),
    )
    status = Column(String, default="placed")
    complete = Column(Boolean)
    pet_ids = relationship("OrderPet", order_by="OrderPet.pet_id", lazy="noload")
    pets = relationship("Pet", secondary=OrderPet.__table__, lazy="noload")

    shipDate = synonym("ship_date")


class PetInOrderDict(TypedDict):
    pet_id: int
    quantity: int
