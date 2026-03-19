from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()


class UserFormRequest(BaseModel):
    pass


@app.post("/process/userform")
async def process_userform(request: UserFormRequest):
    pass
