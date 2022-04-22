"""
API end point
"""
from fastapi import FastAPI, Form
from celery.result import AsyncResult

from tasks import read_plume_data, read_zephyr_data, read_sensor_community_data

app = FastAPI()
func_map = {"plume": read_plume_data,
            "zephyr": read_zephyr_data,
            "sensor_community": read_sensor_community_data}


@app.get("/")
async def landing():
    return "Aston Air Quality API Endpoint"


@app.post("/api/tasks/create/{sensor}")
def create_task(sensor: str, start: float = Form(...), end: float = Form(...)):
    try:
        task = func_map[sensor].delay(start, end)
    except KeyError:
        return {"error": f"unsupported sensor object {sensor}"}
    return {"task_id": task.id}


@app.get("/api/tasks/{task_id}")
def get_result(task_id: str):
    res = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": res.status,
        "task_result": res.result
    }
