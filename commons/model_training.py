from typing import Union
from datetime import datetime
import json
import os
import joblib
import uuid

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from commons.constants import INTERESTING_COLUMN, ALL_PATH, SEED
from commons.model_data_class import ModelMetaData


from memory import Memory

memory = Memory.getInstance()


def saveFittedPipeline(pipeline: Pipeline, uuid: str) -> None:
    """
    Save a fitted pipeline to the models folder

    Args:
        pipeline (Pipeline): The fitted pipeline to be saved
        uuid (str): the uuid of the model
    """
    joblib.dump(pipeline, ALL_PATH.MODELS_FOLDER + uuid + ".joblib")


def train_model(model_input: dict, default_model: bool = False) -> dict:
    """
    Train a model and save it to the models folder
    Add the model meta data to the model meta data file

    Args:
        model_input (dict): The input data for the model. It contains:
            - the model name,
            - the model type
            - the model parameters (actualy the parameters of the model and the tf-idf transformer)
        default_model (bool, optional): If True, the model will be saved as the default model. Defaults to False.

    Returns:
        dict: The model meta data
    """
    df = pd.read_csv(ALL_PATH.DATA_POINTS_FILES)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=SEED)
    model_params = model_input["model_params"]
    model = GradientBoostingClassifier(**model_params["model_params"])
    if "ngram_range" in model_params["tf_idf_params"]:
        model_params["tf_idf_params"]["ngram_range"] = tuple(
            model_params["tf_idf_params"]["ngram_range"]
        )
    tf_idf_transformer = Pipeline(
        [
            ("tf_idf_vectorizer", TfidfVectorizer(**model_params["tf_idf_params"])),
        ]
    )
    preprocess_pipeline = ColumnTransformer(
        [("email_transformer", tf_idf_transformer, INTERESTING_COLUMN.EMAIL_COLUMN)]
    )
    pipeline = Pipeline([("preprocessing", preprocess_pipeline), ("model", model)])
    pipeline.fit(
        train_df[[INTERESTING_COLUMN.EMAIL_COLUMN]], train_df[INTERESTING_COLUMN.TARGET]
    )

    if default_model:
        model_id = "default"
    else:
        model_id = uuid.uuid4().hex

    saveFittedPipeline(pipeline, model_id)

    model_meta_data = ModelMetaData(
        id=model_id,
        name=model_input["name"],
        accuracy=pipeline.score(
            test_df[[INTERESTING_COLUMN.EMAIL_COLUMN]],
            test_df[INTERESTING_COLUMN.TARGET],
        ),
        train_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        serving=False,
        params=model_params,
    )

    save_model_meta_data(model_meta_data)
    return model_meta_data.dict()


def get_all_models() -> Union[dict, None]:
    """
    Get all the registered models meta data

    Returns:
        Union[dict, None]: list of the meta data of all the models registered
    """
    # check if meta data file exists
    if not os.path.exists(ALL_PATH.MODEL_META_DATA_FILE):
        return None
    else:
        with open(ALL_PATH.MODEL_META_DATA_FILE, "r") as file:
            meta_data = json.load(file)
            return meta_data


def get_model_meta_data(id: str) -> dict:
    """
    Get the model meta data for a given id

    Args:
        id (str): _description_

    Returns:
        dict: _description_
    """
    all_models = get_all_models()
    if all_models is None or id not in all_models:
        return None
    else:
        return all_models[id]


def save_model_meta_data(model_meta_data: ModelMetaData) -> bool:
    """
    Add a model meta data to the model meta data file

    Args:
        model_meta_data (ModelMetaData): The model meta data to be saved

    Returns:
        bool: return True if the model meta data was saved successfully
    """
    all_models = get_all_models()
    if all_models is None:
        all_models = {}
    all_models[model_meta_data.id] = model_meta_data.dict()
    with open(ALL_PATH.MODEL_META_DATA_FILE, "w") as file:
        json.dump(all_models, file, indent=4)
    return True


def setup_main_model(id: str) -> None:
    """
    Set the main model to be used for inference

    Args:
    id (str): The id of the model to be used for inference

    """
    all_models = get_all_models()
    if all_models is None or id not in all_models:
        raise Exception(f"Model '{id}' not found")

    old_main_model_id = memory.model_deployed_id
    if old_main_model_id is not None:
        old_main_model = ModelMetaData(**get_model_meta_data(old_main_model_id))
        old_main_model.serving = False
        print(old_main_model)
        save_model_meta_data(old_main_model)

    model_meta_data = ModelMetaData(**all_models[id])
    pipeline = joblib.load(ALL_PATH.MODELS_FOLDER + id + ".joblib")
    model_meta_data.serving = True
    save_model_meta_data(model_meta_data)
    get_model_meta_data
    memory.model_deployed = pipeline
    memory.model_deployed_id = id
