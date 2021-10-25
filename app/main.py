"""
API end point
"""
from fastapi import FastAPI

app = FastAPI()


@app.route("/")
async def landing():
    pass
