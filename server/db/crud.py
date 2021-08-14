from sqlalchemy.orm import Session

from . import models, schemas


def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Note).offset(skip).limit(limit).all()


def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)


def update_note(db: Session, id: int):
    note = db.query(models.Note).get(id)
