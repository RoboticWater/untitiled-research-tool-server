from copy import deepcopy


def note_helper(note) -> dict:
    return {
        "id": str(note['_id']),
        "text": note['text'],
        "created": note['created'],
        "edited": note['edited'],
    }


def make_dict(item) -> dict:
    out = deepcopy(item)
    out["id"] = str(out["_id"])
    del out["_id"]
    return out
