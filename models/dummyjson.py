from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    firstName: str
    lastName: str
    username: str
