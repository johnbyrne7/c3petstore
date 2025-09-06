import datetime
import pytz
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import INCLUDE, fields, post_dump, pre_load, ValidationError, Schema

from models.entities import Pet, Order


class OrderIds(Schema):
    orderId = fields.Integer(attribute="order_id")
    quantity = fields.Integer()


class PetIds(Schema):
    petId = fields.Integer(attribute="pet_id")
    quantity = fields.Integer()


class PetSchema(SQLAlchemyAutoSchema):
    id = auto_field(dump_only=True)

    class Meta:
        model = Pet
        unknown = INCLUDE
        load_instance = False


class OrderSchema(SQLAlchemyAutoSchema):
    id = auto_field(dump_only=True)

    @post_dump(pass_original=True)
    def retPetIds(self, data, original_data, **kwargs):
        data["petIds"] = PetIds(many=True).dump(original_data.pet_ids)
        return data

    @pre_load
    def setPetIds(self, in_data, **kwargs):
        petIds = in_data.pop("petIds", [])
        if petIds:
            in_data["petIds"] = PetIds(many=True).load(petIds)
        return in_data

    @post_dump(pass_original=True)
    def retDate(self, data, original_data, **kwargs):
        data.pop("ship_date")
        data["shipDate"] = original_data.ship_date.strftime("%Y-%m-%d")
        return data

    @pre_load
    def setDate(self, in_data, **kwargs):
        shipDate = in_data.pop("shipDate", None)
        if shipDate:
            try:
                ship_date = datetime.datetime.strptime(shipDate, "%Y-%m-%d")
                pytz.utc.localize(
                    ship_date.replace(hour=0, minute=0, second=0, microsecond=0)
                )
                in_data["ship_date"] = ship_date
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD")
        return in_data

    class Meta:
        model = Order
        unknown = INCLUDE
        load_instance = False
        exclude = (
            "pet_ids",
            "pets",
        )


class OrderPetSchema(OrderSchema):
    @post_dump(pass_original=True)
    def pets(self, data, original_data, **kwargs):
        data["pets"] = PetSchema(many=True).dump(original_data.pets)
        return data
