from pydantic import BaseModel


class HealthData(BaseModel):
    status: str


class ReadyData(BaseModel):
    status: str
    database: str
