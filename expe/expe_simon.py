import time
import requests
import json

SERVICE_POINT = "http://localhost:8005"


def request_api(email: str, timeout=30):
    batch_emb_url = f"{SERVICE_POINT}/prediction/single/fraude@gmail.com"

    res = requests.post(batch_emb_url, headers={"Authorization": "token"}, timeout=3600)
    res_json = json.loads(res.text)

    batch_emb_url_task = f'{SERVICE_POINT}/prediction/tasks/{res_json["task_id"]}'

    task = requests.get(
        batch_emb_url_task, headers={"Authorization": "token"}, timeout=3600
    )

    start_time = time.time()
    while task.status_code == 425:
        if time.time() - start_time > timeout:  # Timeout after 30 seconds
            break
        time.sleep(1)
        task = requests.get(
            batch_emb_url_task, headers={"Authorization": "token"}, timeout=3600
        )
    return task


if __name__ == "__main__":
    email = "fraude@gmail.com"
    result = request_api(email)
    print(result.text)
