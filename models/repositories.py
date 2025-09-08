from multiprocessing import Array
from typing import Optional, Dict, List

from sqlalchemy import sql, Sequence, Select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from starlette import status
from starlette.exceptions import HTTPException

from .entities import Base, Pet, Order, OrderPet
from lib.utils import dictToModel
from .types import PetInOrderDict


class PetRepo:
    @staticmethod
    async def create(session: AsyncSession, data: Dict) -> "Pet":
        pet = dictToModel(data, Pet())
        session.add(pet)
        return pet

    @staticmethod
    async def fetchById(session: AsyncSession, id: int) -> "Pet":
        stmt = sql.select(Pet).where(Pet.id == id)
        # if includeOrders:
        #     stmt = stmt.options(joinedload(Pet.order_ids))
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def fetchAll(
        session: AsyncSession,
        conditions: Optional[Dict] = None,
        limit=10,
        offset=0,
    ) -> Sequence["Pet"]:
        stmt = sql.select(Pet).order_by(Pet.name).limit(limit).offset(offset)
        if conditions:
            # add simple filter conditions if requsted
            stmt = stmt.filter_by(**conditions)
        result = await session.execute(stmt)
        return result.unique().scalars().all()

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
        pet = dictToModel(updated_data, pet)
        return pet

    @staticmethod
    async def delete(session: AsyncSession, id: int, pet: Optional[Pet] = None) -> None:
        if pet:
            await session.delete(pet)
        else:
            stmt = sql.delete(Pet).where(Pet.id == id)
            await session.execute(stmt)

    @staticmethod
    async def getSelect(session: AsyncSession) -> Select:
        stmt = sql.select(Pet)
        return stmt


class OrderRepo:
    #
    #   By default we'll get petIda, but not pets
    #
    @staticmethod
    async def create(
        session: AsyncSession, data: Dict, petIds: List[PetInOrderDict]
    ) -> "Order":
        order = dictToModel(data, Order())
        session.add(order)
        for petId in petIds:
            orderPet = dictToModel(petId, OrderPet())
            order.pet_ids.append(orderPet)
        return order

    @staticmethod
    async def fetchById(
        session: AsyncSession, id: int, includePets: Optional[bool] = None
    ) -> "Order":
        stmt = sql.select(Order).where(Order.id == id)
        stmt = stmt.options(joinedload(Order.pet_ids))
        if includePets:
            stmt = stmt.options(joinedload(Order.pets))
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def fetchAll(
        session: AsyncSession,
        conditions: Optional[Dict] = None,
        petId: Optional[int] = None,
        includePets: Optional[bool] = None,
        limit=10,
        offset=0,
    ) -> Sequence["Order"]:
        stmt = sql.select(Order).order_by(Order.id).limit(limit).offset(offset)
        stmt = stmt.options(joinedload(Order.pet_ids))
        if conditions:
            stmt = stmt.filter_by(**conditions)
        if petId:
            stmt = stmt.join(OrderPet, Order.id == OrderPet.order_id).filter(
                OrderPet.pet_id == petId
            )
        if includePets:
            stmt = stmt.options(joinedload(Order.pets))
        result = await session.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def update(
        session: AsyncSession,
        updated_data: Dict,
        order: Optional[Order] = None,
        petIds: Optional[List[PetInOrderDict]] = None,
    ) -> "Order":
        if not order:
            order = fetchById(session, updated_data.pop("id", 0))
            if order is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                )
        dictToModel(updated_data, order)

        # if we have petIds, delete existing ones, and create new
        if petIds:
            order.pet_ids.clear()
            for petId in petIds:
                orderPet = dictToModel(petId, OrderPet())
                order.pet_ids.append(orderPet)
        return order

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
    async def getSelect(session: AsyncSession) -> Select:
        stmt = sql.select(Order)
        return stmt
