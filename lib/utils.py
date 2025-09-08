from typing import Dict


def format_errors_return(
    errors, status, *, title="Validation Errors", type="Data Errors"
):
    return dict(detail=errors, status=status, title=title, type=type), status


def dictToModel(dict: Dict, model):
    for key, value in dict.items():
        setattr(model, key, value)
    return model
