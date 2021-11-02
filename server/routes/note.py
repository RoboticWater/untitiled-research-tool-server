from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

import db.database

from db.helpers import make_dict
from models.note import *

router = APIRouter()


@router.get("/{id}", response_description="Note retrieved")
async def get_note_data(id):
    try:
        note = await db.database.note_collection.find_one({"_id": ObjectId(id)})
        return ResponseModel(make_dict(note), "Note retrieved successfully")
    except:
        return ErrorResponseModel("An error occured.", 404, "note doesn't exist.")


@router.post("", response_description="Note added into the database")
@router.post("/", response_description="Note added into the database")
async def add_note_data(note: NoteModel = Body(...)):
    print(note)
    note = await db.database.note_collection.insert_one(jsonable_encoder(note))
    print(note)
    new_note = await db.database.note_collection.find_one({"_id": note.inserted_id})
    print(new_note)
    print(make_dict(new_note))
    return ResponseModel(make_dict(new_note), "Note added successfully.")


@router.delete("/{id}", response_description="Note deleted from the database")
async def delete_note_data(id: str):
    try:
        await db.database.note_collection.delete_one({"_id": ObjectId(id)})
        return ResponseModel("Note with ID: {} removed".format(id), "note deleted successfully")
    except:
        return ErrorResponseModel("An error occured", 404, "note with id {0} doesn't exist".format(id))


@router.put("/{id}")
async def update_note(id: str, req: UpdateNoteModel = Body(...)):
    data = req.dict()
    note = await db.database.note_collection.find_one({"_id": ObjectId(id)})
    if not note:
        return ErrorResponseModel("An error occurred", 404, "Note ({}) does not exist.".format(id))
    data["edited"] = datetime.utcnow()
    data["created"] = note["created"]
    db.database.note_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": data})
    return ResponseModel("note with ID: {} name update is successful".format(id), "note name updated successfully")


@router.get("", response_description="notes retrieved")
@router.get("/", response_description="notes retrieved")
async def get_notes():
    notes = [make_dict(note) async for note in db.database.note_collection.find()]
    return ResponseModel(notes, "Notes data retrieved successfully" if len(notes) > 0 else "Empty list returned")
