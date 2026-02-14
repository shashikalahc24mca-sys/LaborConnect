from __future__ import annotations

from typing import List, Optional, Dict, Any

import firebase_admin
from firebase_admin import credentials, db

from .config import settings
from .models import Worker, WorkerCreate, WorkerUpdate


_initialized = False
_init_error: Optional[str] = None

# Message shown when credentials are wrong (e.g. google-services.json used instead of service account key)
_SERVICE_ACCOUNT_HINT = (
    " Use a Service Account key file from Firebase Console: "
    "Project Settings → Service accounts → Generate new private key. "
    "Do not use google-services.json (that is for client apps)."
)


def init_firebase() -> None:
    global _initialized, _init_error
    if _initialized:
        return
    if _init_error:
        raise RuntimeError(_init_error)

    try:
        cred = credentials.Certificate(str("/Users/ritikmakhija/Desktop/Active Projects/tech/LaborConnect/backend/laborconnect-48765-firebase-adminsdk-fbsvc-b609272128.json"))
        firebase_admin.initialize_app(
            cred,
            {"databaseURL": settings.firebase_db_url},
        )
        _initialized = True
    except (ValueError, FileNotFoundError) as e:
        _init_error = (
            f"Invalid Firebase credentials: {e}.{_SERVICE_ACCOUNT_HINT}"
        )
        raise RuntimeError(_init_error)


def _workers_ref():
    init_firebase()
    return db.reference("workers")


def list_workers() -> List[Worker]:
    snapshot: Optional[Dict[str, Any]] = _workers_ref().get()
    if not snapshot:
        return []
    workers: List[Worker] = []
    for worker_id, data in snapshot.items():
        if not isinstance(data, dict):
            continue
        data["id"] = worker_id
        if "createdAt" in data and "created_at" not in data:
            data["created_at"] = data["createdAt"]
        if "ownerUid" in data and "owner_uid" not in data:
            data["owner_uid"] = data["ownerUid"]
        if "portfolioLink" in data and "portfolio_link" not in data:
            data["portfolio_link"] = data["portfolioLink"]
        workers.append(Worker(**data))
    return workers


def get_worker(worker_id: str) -> Optional[Worker]:
    data = _workers_ref().child(worker_id).get()
    if not data:
        return None
    data["id"] = worker_id
    if "createdAt" in data and "created_at" not in data:
        data["created_at"] = data["createdAt"]
    if "ownerUid" in data and "owner_uid" not in data:
        data["owner_uid"] = data["ownerUid"]
    if "portfolioLink" in data and "portfolio_link" not in data:
        data["portfolio_link"] = data["portfolioLink"]
    return Worker(**data)


def create_worker(payload: WorkerCreate) -> Worker:
    ref = _workers_ref().push()
    # pydantic v2 uses `model_dump()` instead of `model_dict()`
    worker = Worker(id=ref.key, **payload.model_dump())
    # Store using camelCase in Firebase but keep snake_case in code
    firebase_payload = {
        "name": worker.name,
        "skill": worker.skill,
        "rating": worker.rating,
        "availability": worker.availability,
        "ownerUid": worker.owner_uid,
        "createdAt": worker.created_at,
        "phone": worker.phone,
        "email": worker.email,
        "portfolioLink": worker.portfolio_link,
    }
    ref.set(firebase_payload)
    return worker


def update_worker(worker_id: str, update: WorkerUpdate) -> Optional[Worker]:
    existing = get_worker(worker_id)
    if not existing:
        return None

    update_data = update.model_dump(exclude_unset=True)
    # Apply updates to existing model
    updated_obj = existing.model_copy(update=update_data)

    firebase_payload = {
        "name": updated_obj.name,
        "skill": updated_obj.skill,
        "rating": updated_obj.rating,
        "availability": updated_obj.availability,
        "ownerUid": updated_obj.owner_uid,
        "createdAt": updated_obj.created_at,
        "phone": updated_obj.phone,
        "email": updated_obj.email,
        "portfolioLink": updated_obj.portfolio_link,
    }
    _workers_ref().child(worker_id).update(firebase_payload)
    return updated_obj


def delete_worker(worker_id: str) -> None:
    _workers_ref().child(worker_id).delete()
