"""
API end point
"""
from fastapi import FastAPI, Form
from celery.result import AsyncResult

from tasks import get_plume_data, get_zephyr_data, get_sensor_community_data, write_plume_to_influx

app = FastAPI()
func_map = {"plume": get_plume_data,
            "zephyr": get_zephyr_data,
            "sensor_community": get_sensor_community_data}


@app.route("/")
async def landing(*args, **kwargs):
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


@app.post("/api/tasks/database/update")
def update_influx_db():
    task = write_plume_to_influx.delay()
    return {"task_id": task.id}
