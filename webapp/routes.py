from fastapi import APIRouter

from webapp.endpoints.model_controler import router as model_controle_rooter
from webapp.endpoints.prediction_controler import router as prediction_controle_rooter


router = APIRouter()
router.include_router(model_controle_rooter)
router.include_router(prediction_controle_rooter)
