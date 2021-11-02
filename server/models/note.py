from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NoteModel(BaseModel):
    text: str = Field(...)
    edited: datetime = Field(default_factory=datetime.utcnow)
    created: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "text": "Example text",
                "created": datetime(2020, 1, 1),
                "edited": datetime(2020, 1, 1)
            }
        }


class UpdateNoteModel(BaseModel):
    text: Optional[str]
    edited: Optional[datetime]
    created: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "text": "Example text",
                "created": datetime(2020, 1, 1),
                "edited": datetime(2020, 1, 1)
            }
        }


def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
