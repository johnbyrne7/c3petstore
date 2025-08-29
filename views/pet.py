from marshmallow import ValidationError

from app import get_session
from models.entities import Pet
from models.repositories import PetRepo
from schemas.schemas import PetSchema

from connexion import NoContent


async def get(_id):
    async with get_session() as session:
        pet = await PetRepo.fetchById(session, _id)
        if not pet:
            return format_errors_return("Pet not found", status=404)
        schema = PetSchema()
        return schema.dump(pet), 200


async def add(body):
    async with get_session() as session:
        schema = (
            PetSchema()
        )  # This is where you could add 'context' to schema if needed
        try:
            data = schema.load(body)
            pet = await PetRepo.create(session, data)
            await session.commit()
            return schema.dump(pet), 201
        except ValidationError as err:
            return format_errors_return(err.messages, 400)


async def update(_id, body):
    async with get_session() as session:
        pet = await PetRepo.fetchById(session, _id)
        if not pet:
            return format_errors_return("Pet not found", status=404)
        schema = PetSchema()
        try:
            # Pass instance in case validations need current attributes
            data = schema.load(body, instance=pet, partial=True)
            pet = await PetRepo.update(session, data, pet)
            await session.commit()
            return schema.dump(pet), 200
        except ValidationError as err:
            return format_errors_return(err.messages, 400)


async def delete(_id):
    async with get_session() as session:
        pet = await PetRepo.fetchById(session, _id)
        if not pet:
            return format_errors_return("Pet not found", status=404)
        await PetRepo.delete(session, _id, pet=pet)
        await session.commit()
        return NoContent, 204


async def find(status=None, name=None):
    async with get_session() as session:
        conditions = {}
        if status:
            conditions["status"] = status
        if name:
            conditions["name"] = name
        pets = await PetRepo.fetchAll(session, conditions)
        return PetSchema(many=True).dump(pets), 200


def format_errors_return(
    errors, status, *, title="Validation Errors", type="Data Errors"
):
    return dict(detail=errors, status=status, title=title, type=type), status
