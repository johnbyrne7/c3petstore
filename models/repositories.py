from typing import Optional, Dict

from sqlalchemy import sql, Sequence, Select
from sqlalchemy.ext.asyncio.session import AsyncSession

from starlette import status
from starlette.exceptions import HTTPException

from .entities import Pet, Order


class PetRepo:
    @staticmethod
    async def create(session: AsyncSession, data: Dict) -> "Pet":
        pet = Pet(**data)
        session.add(pet)
        return pet

    @staticmethod
    async def fetchById(session: AsyncSession, id: int) -> "Pet":
        stmt = sql.select(Pet).where(Pet.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def fetchAll(session: AsyncSession, conditions=None) -> Sequence["Pet"]:
        stmt = sql.select(Pet).order_by(Pet.name)
        if conditions:
            stmt = stmt.filter_by(**conditions)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def delete(session: AsyncSession, id: int, pet: Optional[Pet] = None) -> None:
        if pet:
            await session.delete(pet)
        else:
            stmt = sql.delete(Pet).where(Pet.id == id)
            await session.execute(stmt)

    @staticmethod
    async def update(
        session: AsyncSession, updated_data: Dict, pet: Optional[Pet] = None
    ) -> "Pet":
        if not pet:
            stmt = sql.select(Pet).where(Pet.id == updated_data.pop("id", 0))
            result = await session.execute(stmt)
            pet = result.scalars().first()
            if pet is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found"
                )
        for field, value in updated_data.items():
            setattr(pet, field, value)
        return pet

    @staticmethod
    async def getSelect(session: AsyncSession) -> Select:
        stmt = sql.select(Pet)
        return stmt


class OrderRepo:
    @staticmethod
    async def create(session: AsyncSession, data: Dict) -> "Order":
        order = Order(**data)
        session.add(order)
        return order

    @staticmethod
    async def fetchById(session: AsyncSession, id: int) -> "Order":
        stmt = sql.select(Order).where(Order.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def fetchAll(session: AsyncSession, conditions=None) -> Sequence["Order"]:
        stmt = sql.select(Order).order_by(Order.pet_id)
        if conditions:
            stmt = stmt.filter_by(**conditions)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def delete(
        session: AsyncSession, id: int, order: Optional[Order] = None
    ) -> None:
        if order:
            await session.delete(order)
        else:
            stmt = sql.delete(Order).where(Order.id == id)
            await session.execute(stmt)

    @staticmethod
    async def update(
        session: AsyncSession, updated_data: Dict, order: Optional[Order] = None
    ) -> "Order":
        if not order:
            stmt = sql.select(Order).where(Order.id == updated_data.pop("id", 0))
            result = await session.execute(stmt)
            order = result.scalars().first()
            if order is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                )
        for field, value in updated_data.items():
            setattr(order, field, value)
        return order

    @staticmethod
    async def getSelect(session: AsyncSession) -> Select:
        stmt = sql.select(Order)
        return stmt
