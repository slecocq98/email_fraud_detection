import os
from pydantic import BaseModel


class InterestingColumn(BaseModel):
    """
    The interesting column in the dataset
    """
    EMAIL_COLUMN = "email"
    TARGET = "label"


class AllPaths(BaseModel):
    """
    All the paths used in the project
    """
    PWD = (
        os.getcwd().split("email_fraud_detection")[0]
        + "email_fraud_detection/"
    )
    MODELS_FOLDER = "data/models/"
    DATA_POINTS_FILES = "data/data_points.csv"
    MODEL_META_DATA_FILE = "data/model_meta_data.json"

    def __init__(self) -> None:
        super().__init__()
        for key, value in self.__dict__.items():
            self.__dict__[key] = os.path.join(self.PWD, value)


ALL_PATH = AllPaths()
INTERESTING_COLUMN = InterestingColumn()
SEED = 12

DEFAULT_PARAMS = {
    "model_params": {"n_estimators": 50, "learning_rate": 0.1},
    "tf_idf_params": {
        "ngram_range": (3, 5),
        "strip_accents": "unicode",
        "analyzer": "char",
        "max_features": 500,
        },
    }
