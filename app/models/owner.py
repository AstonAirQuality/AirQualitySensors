from typing import Union

from pydantic import BaseModel


class Owner(BaseModel):
    id: Union[int, None] = -1
    email: str
