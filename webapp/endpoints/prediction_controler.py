from fastapi import APIRouter, HTTPException, Depends
from fastapi.openapi.models import APIKey
from starlette import status

from memory import Memory
from webapp.utils.celery_utils import get_task_info
from webapp.auth_controler import check_auth_token
from workers.tasks import check_one_email_task


memory = Memory.getInstance()

router = APIRouter(
    prefix="/prediction",
    tags=["To make predictions"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/single/{email}",
    summary="Make a prediction for a single email",
    status_code=status.HTTP_201_CREATED,
    response_description="The probability of the email being a fraud",
)
def single_email_prediction(
    email: str,
    api_key: APIKey = Depends(check_auth_token),
) -> dict:
    result = check_one_email_task.delay(email)
    return {"task_id": result.task_id}


@router.get(
    "/tasks/{task_id}",
    summary="Get the status of a task and the result if available",
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
