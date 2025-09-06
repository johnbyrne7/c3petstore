import traceback

from connexion import NoContent
import logging
from connexion.exceptions import ServerError
from marshmallow import ValidationError
from sqlalchemy import sql
from sqlalchemy.orm import joinedload

from lib.utils import format_errors_return
from models.entities import Pet, Order
from models.repositories import PetRepo
from schemas.schemas import PetSchema
from app import get_session

logger = logging.getLogger("app.pet")


async def get(_id):
    logger.debug(f"Fetching pet with id {_id}")
    try:
        async with get_session() as session:
            pet = await PetRepo.fetchById(session, _id)
            if not pet:
                logger.warning(f"Pet not found: id {_id}")
                return format_errors_return("Pet not found", status=404)
            schema = PetSchema()
            return schema.dump(pet), 200
    except Exception as err:
        logger.error(
            f"Server error occurred Fetching pet with id {_id}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError


async def add(body):
    logger.debug(f"Adding pet with data: {body}")
    try:
        async with get_session() as session:
            schema = (
                PetSchema()
            )  # This is where you could add 'context' to schema if needed
            data = schema.load(body)
            pet = await PetRepo.create(session, data)
            await session.commit()
            return schema.dump(pet), 201
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            logger.warning(f"Pet not created with data: {body}")
            return format_errors_return(err.messages, 400)
        logger.error(
            f"Server error occurred Adding pet with data: {body}\n {str(err)}\nTRace:\n{traceback.format_exc()}"
        )
        raise ServerError


async def update(_id, body):
    logger.debug(f"Updating pet with id: {_id}, body: {body}")
    try:
        async with get_session() as session:
            pet = await PetRepo.fetchById(session, _id)
            if not pet:
                return format_errors_return("Pet not found", status=404)
            schema = PetSchema()
            # Pass instance in case validations need current attributes
            data = schema.load(body, instance=pet, partial=True)
            pet = await PetRepo.update(session, data, pet)
            await session.commit()
            logger.debug(f"Pet updated with id: {_id}")
            pet = await PetRepo.fetchById(session, _id)  # get updated Pet from db
            return schema.dump(pet), 200
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            logger.warning(f"Pet not updated with id: {_id}")
            return format_errors_return(err.messages, 400)
        logger.error(
            f"Server error occurred Updating pet with id: {_id}, body: {body}\n {str(err)}\nTRace:\n{traceback.format_exc()}"
        )
        raise ServerError


async def delete(_id):
    logger.debug(f"Deleting pet with id {_id}")
    try:
        async with get_session() as session:
            pet = await PetRepo.fetchById(session, _id)
            if not pet:
                logger.warning(f"Pet not found for delete: id {_id}")
                return format_errors_return("Pet not found", status=404)
            await PetRepo.delete(session, _id, pet=pet)
            await session.commit()
            return NoContent, 204
    except Exception as err:
        logger.error(
            f"Server error occurred Deleting pet with id {_id}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError


async def find(status=None, name=None, offset=0, limit=10):
    logger.debug(f"Finding pets with status: {status}, name: {name}")
    try:
        async with get_session() as session:
            # No need to validate limits as C3 does that
            conditions = {}
            if status:
                conditions["status"] = status
            if name:
                conditions["name"] = name
            pets = await PetRepo.fetchAll(
                session,
                conditions=conditions,
                limit=limit,
                offset=offset,
            )
            schema = PetSchema(many=True)
            return schema.dump(pets), 200
    except Exception as err:
        logger.error(
            f"Server error occurred Finding pets with status: {status}, name: {name}\n {str(err)}\n{traceback.format_exc()}"
        )
        raise ServerError
