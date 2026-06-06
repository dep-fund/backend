from pydantic import BaseModel, ConfigDict


class ProjectImageResponse(BaseModel):
    number: int
    url: str

    model_config = ConfigDict(from_attributes=True)
