from typing import Any, Dict


# PUBLIC_INTERFACE
def to_public_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB internal _id field to public id string form.

    Note:
        We are storing string IDs in most collections to avoid ObjectId coercion. If any
        collection uses ObjectId, convert here using str(doc["_id"]).
    """
    if not doc:
        return doc
    if "_id" in doc:
        doc = doc.copy()
        doc["id"] = str(doc.pop("_id"))
    return doc
