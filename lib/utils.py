
from typing import Dict, TypedDict


def format_errors_return(
        errors, status, *, title="Validation Errors", type="Data Errors"
):
    return dict(detail=errors, status=status, title=title, type=type), status


def dictToModel(dict: Dict, model):
    for key, value in dict.items():
        setattr(model, key, value)
    return model

class PetInOrderDict(TypedDict):
    pet_id: int
    quantity: int
