from typing import Union

from pydantic import BaseModel


class PlumePlatform(BaseModel):
    id: Union[int, None] = -1
    name: str
    serial_number: str
    email: str
    password: str
    owner_email: Union[str, None] = ""
    owner_id: Union[int, None] = -1  # -1 means no owner specified
    sync_status: str = "unknown"
