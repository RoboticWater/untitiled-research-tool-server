import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    text: str


class Note(BaseModel):
    id: int
    text: str
    created: datetime = datetime.datetime.utcnow
