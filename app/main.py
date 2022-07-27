import os
from typing import Optional

import mysql.connector
import uvicorn
from fastapi import FastAPI, Form, Request
from celery.result import AsyncResult
from fastapi.templating import Jinja2Templates
from mysql.connector import IntegrityError
from starlette import status
from starlette.responses import RedirectResponse

from app.daos.owner_dao import OwnerDAO
from app.models.owner import Owner
from app.models.plume_platform import PlumePlatform
from app.services.owner_service import OwnerService
from validators.plume_platform_validator import PlumePlatformValidator, InvalidSerialNumberException, \
    InvalidEmailException
from services.plume_service import PlumeService
from daos.plume_dao import PlumeDAO
from tasks import read_plume_data, read_zephyr_data, read_sensor_community_data

app = FastAPI()
templates = Jinja2Templates(directory="views")

connection = mysql.connector.connect(
    port=os.environ.get("DATABASE_PORT"),
    host=os.environ.get("DATABASE_HOST"),
    user=os.environ.get("DATABASE_USERNAME"),
    password=os.environ.get("DATABASE_PASSWORD"),
    database=os.environ.get("DATABASE_NAME")
)

func_map = {"plume": read_plume_data,
            "zephyr": read_zephyr_data,
            "sensor_community": read_sensor_community_data}

plume_service = PlumeService(PlumeDAO(connection))
plume_validator = PlumePlatformValidator()

owner_service = OwnerService(OwnerDAO(connection))

links = ["/docs", "/owners", "/plume-platforms"]


@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "links": links})


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


@app.get("/plume-platforms")
async def get_platforms(request: Request):
    return templates.TemplateResponse("plume-platforms.html",
                                      {"request": request,
                                       "platforms": list(plume_service.get_platforms()),
                                       "owners": owner_service.get_owners()})


@app.post("/plume-platforms")
def add_platform(request: Request,
                 name: str = Form(...),
                 serial_number: str = Form(...),
                 email: str = Form(...),
                 password: str = Form(...),
                 owner_id: Optional[int] = Form(...)):
    platform = PlumePlatform(name=name, serial_number=serial_number, email=email, password=password, owner_id=owner_id)
    error = None
    try:
        if plume_validator.is_valid(platform):
            plume_service.add_platform(platform)
    except (InvalidSerialNumberException, InvalidEmailException) as e:
        error = e
    except IOError:
        error = "Internal Server Error: Unable to add platform"

    return templates.TemplateResponse("plume-platforms.html",
                                      {"request": request,
                                       "error": error,
                                       "platforms": list(plume_service.get_platforms()),
                                       "owners": owner_service.get_owners()})


@app.get("/plume-platforms/{platform_id}")
def get_platform(request: Request, platform_id: int):
    try:
        return templates.TemplateResponse("plume-platform.html",
                                          {"request": request,
                                           "platform": plume_service.get_platform(platform_id),
                                           "owners": owner_service.get_owners()})
    except IOError:
        return RedirectResponse("/plume-platforms")


@app.post("/plume-platforms/update")
def modify_platform(name: str = Form(...),
                    serial_number: str = Form(...),
                    email: str = Form(...),
                    password: str = Form(...),
                    owner_id: int = Form(...),
                    platform_id: int = Form(...)):
    platform = PlumePlatform(id=platform_id, name=name, serial_number=serial_number, email=email, password=password,
                             owner_id=owner_id)
    try:
        if plume_validator.is_valid(platform):
            plume_service.modify_platform(platform)
    except (InvalidSerialNumberException, InvalidEmailException, IOError) as e:
        return RedirectResponse(f"/plume-platforms/{platform_id}", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(f"/plume-platforms", status_code=status.HTTP_302_FOUND)


@app.post("/plume-platforms/delete")
def delete_platform(platform_id: int = Form(...)):
    plume_service.delete_platform(platform_id)
    return RedirectResponse(f"/plume-platforms", status_code=status.HTTP_302_FOUND)


@app.get("/owners")
def get_owners(request: Request):
    return templates.TemplateResponse("owners.html",
                                      {"request": request,
                                       "owners": owner_service.get_owners()})


@app.post("/owners")
def add_owner(request: Request, email: str = Form(...)):
    error = None
    try:
        owner_service.add_owner(Owner(email=email))
    except (IntegrityError, IOError):
        error = "Internal Server Error: Unable to add owner"

    return templates.TemplateResponse("owners.html",
                                      {"request": request,
                                       "error": error,
                                       "owners": owner_service.get_owners()})


@app.get("/owners/{owner_id}")
def get_owner(request: Request, owner_id: int):
    try:
        return templates.TemplateResponse("owner.html",
                                          {"request": request,
                                           "owner": owner_service.get_owner(owner_id)})
    except IOError:
        return RedirectResponse("/owners")


@app.post("/owners/delete")
def delete_owner(request: Request, owner_id: int = Form(...)):
    try:
        owner_service.delete_owner(owner_id)
        return RedirectResponse("/owners", status_code=status.HTTP_302_FOUND)
    except IntegrityError:
        return templates.TemplateResponse("owner.html",
                                          {"request": request,
                                           "error": "Unable to delete owner as it currently has assigned sensors",
                                           "owner": owner_service.get_owner(owner_id)})


@app.post("/owners/update")
def update_owner(owner_id: int = Form(...), email: str = Form(...)):
    # TODO: owner validator
    owner = Owner(id=owner_id, email=email)
    owner_service.replace_owner(owner)
    return RedirectResponse("/owners", status_code=status.HTTP_302_FOUND)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
