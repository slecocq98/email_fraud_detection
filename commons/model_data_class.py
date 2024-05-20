from pydantic import BaseModel
from enum import Enum


class ModelMetaData(BaseModel):
    id: str
    name: str
    accuracy: float
    train_date: str
    serving: bool
    params: dict


class ModelTypes(str, Enum):
    """
    Enum for the model types actually handled by the pipeline.
    """

    GradientBoosting = "GradientBoosting"


class ModelParams(BaseModel):

    model_params: dict
    tf_idf_params: dict


class ModelInput(BaseModel):
    name: str
    model_type: ModelTypes
    model_params: ModelParams
