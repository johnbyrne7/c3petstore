import traceback

from connexion import NoContent
import logging

from connexion.exceptions import ServerError
from marshmallow import ValidationError

from app import get_session
from models.entities import Order
from models.repositories import OrderRepo, PetRepo
from schemas.schemas import OrderSchema

logger = logging.getLogger("app.order")


async def get(_id):
    logger.debug(f"Fetching order with id {_id}")
    try:
        async with get_session() as session:
            order = await OrderRepo.fetchById(session, _id)
            if not order:
                return format_errors_return("Order not found", status=404)
            schema = OrderSchema()
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
            pet = await PetRepo.fetchById(session, data["pet_id"])
            #  validate pet_id
            if not pet:
                return format_errors_return(
                    f"Invalid petId: Pet {data['pet_id']} does not exist", status=400
                )
            order = await OrderRepo.create(session, data)
            await session.commit()
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
            #  validate pet_id if passed and changed
            pet_id = data.get("pet_id", None)
            if type(pet_id) == int and pet_id != order.pet_id:
                pet = await PetRepo.fetchById(session, pet_id)
                if not pet:
                    return format_errors_return(
                        f"Invalid petId: Pet {data['pet_id']} does not exist",
                        status=400,
                    )
            order = await OrderRepo.update(session, data, order)
            await session.commit()
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


async def find(petId=None, status=None, offset=0, limit=10):
    logger.debug(f"Finding orders with status: {status}, petId: {petId}")
    try:
        async with get_session() as session:
            if limit < 1 or limit > 100:
                return format_errors_return(
                    "Limit must be between 1 and 100", status=400
                )
            if offset < 0:
                return format_errors_return("Offset must be non-negative", status=400)
            schema = OrderSchema(many=True)
            conditions = {}
            if petId:
                conditions["pet_id"] = petId
            if status:
                conditions["status"] = status
            orders = await OrderRepo.fetchAll(
                session, conditions=conditions, limit=limit, offset=offset
            )
            return schema.dump(orders), 200
    except Exception as err:
        logger.error(
            f"Server error occurred Finding orders with status: {status}, petId: {petId}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError


def format_errors_return(
    errors, status, *, title="Validation Errors", type="Data Errors"
):
    return dict(detail=errors, status=status, title=title, type=type), status
