import pandas as pd
from memory import Memory
from worker import celery

from commons.model_training import train_model, setup_main_model

memory = Memory.getInstance()


@celery.task(shared=True, max_retries=3)
def train_model_task(params: dict):
    return train_model(params, default_model=False)


@celery.task(shared=True, max_retries=3)
def check_one_email_task(email: str):
    result = memory.model_deployed.predict_proba(pd.DataFrame([{"email": email}]))[0][0]
    return {"proba": result, "email": email}


@celery.task(shared=True, max_retries=3)
def setup_main_model_task(model_id: str):
    return setup_main_model(model_id)
