from marshmallow import ValidationError

from app import get_session
from models.entities import Order
from models.repositories import OrderRepo, PetRepo
from schemas.schemas import OrderSchema

from connexion import NoContent


async def get(_id):
    async with get_session() as session:
        order = await OrderRepo.fetchById(session, _id)
        if not order:
            return format_errors_return("Order not found", status=404)
        return OrderSchema().dump(order), 200


async def add(body):
    async with get_session() as session:
        data = OrderSchema().load(body)
        pet = await PetRepo.fetchById(session, data["pet_id"])
        #  validate pet_id
        if not pet:
            return format_errors_return(
                f"Invalid petId: Pet {data['pet_id']} does not exist", status=400
            )
        try:
            order = await OrderRepo.create(session, data)
            await session.commit()
            return OrderSchema().dump(order), 201
        except ValidationError as err:
            return format_errors_return(err.messages, 400)


async def update(_id, body):
    async with get_session() as session:
        order = await OrderRepo.fetchById(session, _id)
        if not order:
            return format_errors_return("Order not found", status=404)
        try:
            data = OrderSchema().load(body, instance=order, partial=True)
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
            return OrderSchema().dump(order), 200
        except ValidationError as err:
            return format_errors_return(err.messages, 400)


async def delete(_id):
    async with get_session() as session:
        order = await OrderRepo.fetchById(session, _id)
        if not order:
            return format_errors_return("Order not found", status=404)
        await OrderRepo.delete(session, _id, order=order)
        await session.commit()
        return NoContent, 204


async def find(petId=None, status=None):
    async with get_session() as session:
        conditions = {}
        if petId:
            conditions["pet_id"] = petId
        if status:
            conditions["status"] = status
        orders = await OrderRepo.fetchAll(session, conditions)
        return OrderSchema(many=True).dump(orders), 200


def format_errors_return(
    errors, status, *, title="Validation Errors", type="Data Errors"
):
    return dict(detail=errors, status=status, title=title, type=type), status
