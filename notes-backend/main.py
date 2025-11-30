# -----------------------------------------------------------------------------
# Author: Afu Tse
# GitHub Repo: https://github.com/r3xakead0/gcp-notes-app-serverless
# Description: Notes API with Firestore for Google Cloud Functions
# -----------------------------------------------------------------------------

import json
import datetime
from google.cloud import firestore

db = firestore.Client()
NOTES_COLLECTION = "notes"

def _get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

def _note_to_dict(doc):
    data = doc.to_dict()
    data["id"] = doc.id
    return data

def notes_api(request):
    # CORS
    if request.method == "OPTIONS":
        return ("", 204, _get_cors_headers())

    headers = _get_cors_headers()
    method = request.method

    path = request.path or "/"
    segments = [seg for seg in path.split("/") if seg]

    is_collection = False
    note_id = None

    if len(segments) == 0:
        is_collection = True              # "/"
    elif len(segments) == 1 and segments[0] == "notes":
        is_collection = True              # "/notes"
    elif len(segments) == 2 and segments[0] == "notes":
        note_id = segments[1]             # "/notes/{id}"
    else:
        return (json.dumps({"error": "Not found"}), 404, headers)

    try:
        # GET list or detail
        if method == "GET":
            if is_collection:
                docs = (
                    db.collection(NOTES_COLLECTION)
                    .order_by("created_at", direction=firestore.Query.DESCENDING)
                    .stream()
                )
                notes = [_note_to_dict(d) for d in docs]
                return (json.dumps(notes), 200, headers)
            else:
                doc = db.collection(NOTES_COLLECTION).document(note_id).get()
                if not doc.exists:
                    return (json.dumps({"error": "Note not found"}), 404, headers)
                return (json.dumps(_note_to_dict(doc)), 200, headers)

        # POST create
        if method == "POST" and is_collection:
            payload = request.get_json(silent=True)
            if not payload or "title" not in payload:
                return (json.dumps({"error": "Invalid JSON"}), 400, headers)

            now = datetime.datetime.utcnow().isoformat() + "Z"

            doc_ref = db.collection(NOTES_COLLECTION).document()
            doc_ref.set({
                "title": payload["title"],
                "detail": payload.get("detail", ""),
                "created_at": now,
                "updated_at": now
            })

            return (json.dumps(_note_to_dict(doc_ref.get())), 201, headers)

        # PUT update
        if method in ("PUT", "PATCH") and note_id:
            payload = request.get_json(silent=True)
            if not payload:
                return (json.dumps({"error": "Invalid JSON"}), 400, headers)

            doc_ref = db.collection(NOTES_COLLECTION).document(note_id)
            if not doc_ref.get().exists:
                return (json.dumps({"error": "Note not found"}), 404, headers)

            updates = {
                "updated_at": datetime.datetime.utcnow().isoformat() + "Z"
            }
            if "title" in payload:
                updates["title"] = payload["title"]
            if "detail" in payload:
                updates["detail"] = payload["detail"]

            doc_ref.update(updates)
            return (json.dumps(_note_to_dict(doc_ref.get())), 200, headers)

        # DELETE remove
        if method == "DELETE" and note_id:
            doc_ref = db.collection(NOTES_COLLECTION).document(note_id)
            if not doc_ref.get().exists:
                return (json.dumps({"error": "Note not found"}), 404, headers)
            doc_ref.delete()
            return (json.dumps({"message": "Note deleted"}), 200, headers)

        return (json.dumps({"error": "Method not allowed"}), 405, headers)

    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, headers)
