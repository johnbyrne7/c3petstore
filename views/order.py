import traceback

from connexion import NoContent
import logging

from connexion.exceptions import ServerError
from marshmallow import ValidationError

from app import get_session
from lib.utils import format_errors_return
from models.entities import Order
from models.repositories import OrderRepo, PetRepo
from schemas.schemas import OrderSchema, OrderPetSchema

logger = logging.getLogger("app.order")


async def get(_id, includePets=None):
    logger.debug(f"Fetching order with id {_id}")
    try:
        async with get_session() as session:
            includePets = "yes" == includePets
            order = await OrderRepo.fetchById(session, _id, includePets=includePets)
            if not order:
                return format_errors_return("Order not found", status=404)
            schema = OrderPetSchema() if includePets else OrderSchema()
            return schema.dump(order), 200
    except Exception as err:
        logger.error(
            f"Server error occurred Fetching order with id {_id}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError


async def add(body):
    logger.debug(f"Adding order with data: {body}")
    try:
        async with get_session() as session:
            schema = (
                OrderSchema()
            )  # This is where you could add 'context' to schema if needed
            data = schema.load(body)
            petIds = data.get(
                "petIds", []
            )  # The route spec requires at least one petId

            #  We perform all database validations in the view, after the schema has formatted the data
            for petId in petIds:
                pet = await PetRepo.fetchById(session, petId["pet_id"])
                if not pet:
                    return format_errors_return(
                        f"Invalid petId: Pet {petId['pet_id']} does not exist",
                        status=400,
                    )

            order = await OrderRepo.create(session, data, petIds=petIds)
            await session.commit()
            order = await OrderRepo.fetchById(
                session, order.id
            )  # get updated order from db
            return schema.dump(order), 201
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            logger.warning(f"Order not created with data: {body}")
            return format_errors_return(err.messages, 400)
        logger.error(
            f"Server error occurred Adding order with data: {body}\n {str(err)}\nTRace:\n{traceback.format_exc()}"
        )
        raise ServerError


async def update(_id, body):
    logger.debug(f"Updating pet with id: {_id}, body: {body}")
    try:
        async with get_session() as session:
            order = await OrderRepo.fetchById(session, _id)
            if not order:
                return format_errors_return("Order not found", status=404)
            schema = OrderSchema()
            # Pass instance in case validations need current attributes
            data = schema.load(body, instance=order, partial=True)

            #  validate pet_ids if passed and changed
            orderPetIds = [petId.pet_id for petId in order.pet_ids]
            petIds = data.pop("petIds", [])
            for petId in petIds:
                if petId["pet_id"] not in orderPetIds:
                    pet = await PetRepo.fetchById(session, petId["pet_id"])
                    if not pet:
                        return format_errors_return(
                            f"Invalid petId: Pet {petId['pet_id']} does not exist",
                            status=400,
                        )

            order = await OrderRepo.update(session, data, order=order, petIds=petIds)
            await session.commit()
            order = await OrderRepo.fetchById(
                session, order.id
            )  # get updated order from db
            return schema.dump(order), 200
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            logger.warning(f"Order not updated with id: {_id}")
            return format_errors_return(err.messages, 400)
        logger.error(
            f"Server error occurred Updating order with id: {_id}, body: {body}\n {str(err)}\nTRace:\n{traceback.format_exc()}"
        )
        raise ServerError


async def delete(_id):
    logger.debug(f"Deleting pet with id {_id}")
    try:
        async with get_session() as session:
            order = await OrderRepo.fetchById(session, _id)
            if not order:
                return format_errors_return("Order not found", status=404)
            await OrderRepo.delete(session, _id, order=order)
            await session.commit()
            return NoContent, 204
    except Exception as err:
        logger.error(
            f"Server error occurred Deleting order with id {_id}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError


async def find(petId=None, status=None, includePets=None, offset=0, limit=10):
    logger.debug(f"Finding orders with status: {status}, petId: {petId}")
    try:
        async with get_session() as session:
            includePets = "yes" == includePets
            # No need to validate limit, offset as C3 does that
            schema = (
                OrderPetSchema(many=True) if includePets else OrderSchema(many=True)
            )
            conditions = {}
            if status:
                conditions["status"] = status
            orders = await OrderRepo.fetchAll(
                session,
                petId=petId,
                conditions=conditions,
                includePets=includePets,
                limit=limit,
                offset=offset,
            )
            return schema.dump(orders), 200
    except Exception as err:
        logger.error(
            f"Server error occurred Finding orders with status: {status}, petId: {petId}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError
