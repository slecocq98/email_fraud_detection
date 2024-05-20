from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.openapi.models import APIKey
from starlette import status
from commons.model_data_class import ModelInput, ModelMetaData

from memory import Memory
from webapp.utils.celery_utils import get_task_info
from webapp.auth_controler import check_auth_token
from workers.tasks import train_model_task, setup_main_model_task
from commons.model_training import get_all_models, get_model_meta_data

memory = Memory.getInstance()


router = APIRouter(
    prefix="/model",
    tags=["To manage the models in the system"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/train",
    summary="train a new model",
    status_code=status.HTTP_201_CREATED,
    response_description="The metadata of the new model",
)
def model_training(
    model_input: ModelInput,
    api_key: APIKey = Depends(check_auth_token),
) -> dict:
    result = train_model_task.delay(model_input.dict())
    return {
        "task_id": result.task_id,
        "message": f"Model '{model_input.name}' of type '{model_input.model_type}' received and will be trained.",
    }


@router.get(
    "/registry/all",
    summary="Get all the models",
    status_code=status.HTTP_200_OK,
    response_description="List of metadata of all the models",
    response_model=List[ModelMetaData],
)
def get_all_models_registered(
    api_key: APIKey = Depends(check_auth_token),
) -> List[dict]:
    all_model = get_all_models()
    if not all_model:
        return []
    return list(all_model.values())


@router.get(
    "/registry/{model_id}",
    summary="Get a specific model",
    status_code=status.HTTP_200_OK,
    response_description="The metadata of the model",
    response_model=ModelMetaData,
)
def get_model(
    model_id: str,
    api_key: APIKey = Depends(check_auth_token),
) -> dict:
    model = get_model_meta_data(model_id)
    if not model:
        raise HTTPException(
            detail="Model Not found", status_code=status.HTTP_404_NOT_FOUND
        )
    return model


@router.put(
    "/set_main/{model_id}",
    summary="Set the main model used in rooter predict",
    status_code=status.HTTP_200_OK,
    response_description="If the model is successfully set as main",
)
def set_main_model(
    model_id: str,
    api_key: APIKey = Depends(check_auth_token),
) -> dict:
    if model_id not in get_all_models():
        raise HTTPException(
            detail="Model Not found", status_code=status.HTTP_404_NOT_FOUND
        )
    try:
        task_result = setup_main_model_task.delay(model_id)

        task_result.get()

        return {"message": f"Model '{model_id}' is now the main model for prediction."}
    except Exception as e:
        raise HTTPException(
            detail=f"Error setting the model as main: {e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get(
    "/tasks/{task_id}",
    summary="Get the status of a task and if available the result",
)
def get_task(
    task_id: str,
    api_key: APIKey = Depends(check_auth_token),
):
    task_info = get_task_info(task_id)
    if not task_info or "task_status" not in task_info:
        raise HTTPException(
            detail="Task Not found", status_code=status.HTTP_404_NOT_FOUND
        )

    if (
        task_info["task_status"] in ["FAILURE", "SUCCESS"]
        and "task_result" in task_info
    ):
        return task_info["task_result"]

    if task_info["task_status"] in ["STARTED", "PENDING"]:
        raise HTTPException(
            detail=f"Task is {task_info['task_status']}",
            status_code=status.HTTP_425_TOO_EARLY,
        )

    raise HTTPException(
        detail="Task is Running, Pending or Cancelled",
        status_code=status.HTTP_400_BAD_REQUEST,
    )
