# Email fraud detection service

This work was done for an interview. At the end of the readme you have ta report on the work done, way of improvement and how I would do differently

## Project architecture

- `app.py` sets up a FastAPI application
- `worker.py` sets up Celery
- `memory.py` implements the Singleton design pattern
- In the folder `data/`, there are all the models, the train_data, and a list of the meta-data of the models
- In `common/`, there are the constants, the Pydantic class for the data (input, BD), and the function used to monitor the model (used in the initialization of the Celery instance and the celery_task)
- In `exp/`, there is a script to test the inference of the model
- In `webapp/`, all the routes needed which call celery task or a simple function to get data
- In `worker/`:
    - `__init__.py` sets up the default model to deploy (train it if it doesn't exist)
    - `task.py` defines all the tasks that run asynchronously

## To Run the App

You need to first create a virtual environment (venv) and install the required packages.

```sh
python3 -m venv .venv
```

Then
```sh
source .venv/bin/activate
cd email_fraud_detection
pip install -r requirements.txt
```

To run the app, you need to have MongoDB and RabbitMQ installed. To set up MongoDB and RabbitMQ, you can run:

```sh
docker compose up
```

Then you need to run 2 scripts 

```sh
python3 -m gunicorn app:app --name email-fraud-detection  --bind 0.0.0.0:8005 --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 3600 --log-level debug --access-logfile - --error-logfile -
```

and in another terminal 
```sh
python3 -m celery -A worker.celery worker --loglevel=info --pool=solo -Q queue -c 1
```
>In production, you can use `pool=prefork` to utilize multiple processors.

>If you're using Visual Studio Code, two debuggers are set up to run Gunicorn and Celery in `.vscode/launch.json`.

## The routes

You can find all the query on http://localhost:8005/docs


### To make a prediction
The test the inference run `email_fraud_detection/expe/expe_simon.py` 

To launch the inference with curl
```
curl --request POST \
  --url http://localhost:8005/prediction/single/fraude@gmail.com \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'

//returns
{
	"task_id": <uuid>
}
  ```

To retrieve the task state and, if it has finished, the task result.

```
curl --request GET \
  --url http://localhost:8005/prediction/tasks/4e8f7a2a-4659-4dd9-954c-4f2d4ce1ee48 \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'

//returns
{
	"proba": 0.9346938678972994,
	"email": "fraude@gmail.com"
}
```

### For model control

**When we launch the application, a first default model is trained and deployed**

As JSON does not support tuples, "ngram-range" is written as a list of two elements (for input and output).

To get all the models
```
curl --request GET \
  --url http://localhost:8005/model/registry/all \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'

//returns
[
	{
		"id": "default",
		"name": "default",
		"accuracy": 0.943,
		"train_date": "2024-03-10 23:28",
		"serving": false,
		"params": {
			"model_params": {
				"n_estimators": 50,
				"learning_rate": 0.1
			},
			"tf_idf_params": {
				"ngram_range": [
					3,
					5
				],
				"strip_accents": "unicode",
				"analyzer": "char",
				"max_features": 500
			}
		}
	},
	{
		"id": "491075e4a68f42089c997802497e3996",
		"name": "test1",
		"accuracy": 0.993,
		"train_date": "2024-03-10 23:29",
		"serving": true,
		"params": {
			"model_params": {
				"n_estimators": 50,
				"learning_rate": 0.1
			},
			"tf_idf_params": {
				"ngram_range": [
					1,
					3
				],
				"strip_accents": "unicode",
				"analyzer": "char",
				"max_features": 500
			}
		}
	}
]
```

To get one 
```
curl --request GET \
  --url http://localhost:8005/model/registry/default \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'

//returns
{
	"id": "default",
	"name": "default",
	"accuracy": 0.943,
	"train_date": "2024-03-10 23:28",
	"serving": true,
	"params": {
		"model_params": {
			"n_estimators": 50,
			"learning_rate": 0.1
		},
		"tf_idf_params": {
			"ngram_range": [
				3,
				5
			],
			"strip_accents": "unicode",
			"analyzer": "char",
			"max_features": 500
		}
	}
}
```

To train a new model
```
curl --request POST \
  --url http://localhost:8005/model/train \
  --header 'Authorization: token' \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/8.4.0' \
  --data '{
	"name":"test1",
	"model_type":"GradientBoosting",
	"model_params":{
    "model_params": {"n_estimators": 50, "learning_rate": 0.1},
    "tf_idf_params": {
        "ngram_range": [1, 3],
        "strip_accents": "unicode",
        "analyzer": "char",
        "max_features": 500
    }
	}
}
//returns
{
	"task_id": "642d158f-0e4e-431a-a5d6-f744f1b2f525",
	"message": "Model 'test1' of type 'GradientBoosting' received and will be trained."
}
```

To know if a model is trained

```
curl --request GET \
  --url http://localhost:8005/model/tasks/4cf15399-88ff-4faf-a9cd-c738f0f9856a \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'

//returns
{
	"id": "7ae14bb66c754e099a001f4c60c781dd",
	"name": "test1",
	"accuracy": 0.993,
	"train_date": "2024-03-10 00:00:00",
	"serving": false,
	"params": {
		"model_params": {
			"n_estimators": 50,
			"learning_rate": 0.1
		},
		"tf_idf_params": {
			"ngram_range": [
				1,
				3
			],
			"strip_accents": "unicode",
			"analyzer": "char",
			"max_features": 500
		}
	}
}
```


To set a model, you have to do it using its id.
```
curl --request PUT \
  --url http://localhost:8005/model/set_main/491075e4a68f42089c997802497e3996 \
  --header 'Authorization: token' \
  --header 'User-Agent: insomnia/8.4.0'
//returns
{
	"message": "Model '491075e4a68f42089c997802497e3996' is now the main model for prediction."
}
```


# Report on API Modifications and Areas for Improvement
I placed myself in a more realistic scenario with a large number of users. It seemed more pertinent to use well-known frameworks for asynchronous processing, parallelism, and queue management: FastAPI and Celery.

## The missing steps for production deployment are:

- Better explanation of the repository architecture.
- Update the frameworks (Celery is slightly outdated).
- Improved robustness regarding inputs (especially on model parameters with more elaborate Pydantic classes).
- Better error management (capturing, logging).
- Better management of shared memory as there are modifications (the instance memory), with Redis for example, or sharing middleware. Also, consider changing the instance memory (see what I would have done differently).
- Depending on the security standards used, another authentication protocol if needed. Check whether both @app.middleware("http") and webapp.py/auth_controller.py are necessary.
- Unit tests + integration tests + API tests (especially on the expected results for a given model).
- Complete the creation of the Dockerfile.
- Set up CI/CD and container orchestration (AWS ECS, for example).
- Use Amazon RDS for MongoDB and RabbitMQ.
- Test in development (or staging) before production deployment.
- Consider implementing monitoring and alerts to track model performance, and record model behaviors.
- Cost reduction by implementing stop_worker and start_worker if this API is used sporadically.


## What I Would Have Done Differently:

- No model training directly within the application, and an output label rather than a score. Instead, train the model beforehand, then store it (on Amazon S3, for example), and download it in the application at initialization. The reasons:
- Better model selection, results analysis, and threshold selection.
- Better monitoring (we know which model is used at what time due to task definitions).
- Fewer resources needed as there is no training.
- Consider the data pipeline in advance. Do we want to process the entire database or handle each new address directly (fewer resources allocated if it is occasional control)?



