import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Pet(Base):
    __tablename__ = "pet"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default="available")


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pet.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer)
    ship_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )
    status = Column(String, default="placed")
    complete = Column(Boolean)

    petId = synonym("pet_id")
    shipDate = synonym("ship_date")
