import sys

from memory import Memory

from commons.model_training import get_all_models, setup_main_model, train_model
from commons.constants import DEFAULT_PARAMS
from commons.model_data_class import ModelInput, ModelTypes

memory = Memory.getInstance()

# Worker loading only for workers
is_worker = "worker" in sys.argv
if is_worker:
    all_models = get_all_models()

    if all_models is None or "default" not in all_models:
        model_input = ModelInput(
            name="default",
            model_type=ModelTypes.GradientBoosting,
            model_params=DEFAULT_PARAMS,
        ).dict()
        _ = train_model(model_input=model_input, default_model=True)

    setup_main_model("default")
