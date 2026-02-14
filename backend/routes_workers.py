from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from .firebase_client import (
    list_workers as fb_list_workers,
    get_worker as fb_get_worker,
    create_worker as fb_create_worker,
    update_worker as fb_update_worker,
    delete_worker as fb_delete_worker,
)
from .models import Worker, WorkerCreate, WorkerUpdate, RecommendationResult


router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=List[Worker])
def list_workers() -> List[Worker]:
    return fb_list_workers()


@router.post("/", response_model=Worker, status_code=201)
def create_worker(worker: WorkerCreate) -> Worker:
    return fb_create_worker(worker)


@router.get("/recommend", response_model=RecommendationResult)
def recommend_workers(
    skill: str = Query(..., description="Desired worker skill, e.g. Mason, Carpenter"),
    limit: int = Query(5, ge=1, le=50),
) -> RecommendationResult:
    """
    Simple rule-based recommendation:
    1. Filter workers by matching skill (case-insensitive).
    2. Sort by rating (desc), then availability (Available first), then created_at (newer first).
    This mimics a basic machine-learning ranking model using human-defined rules.
    """
    all_workers = fb_list_workers()
    skill_lower = skill.lower().strip()

    filtered = [
        w
        for w in all_workers
        if w.skill.lower().strip() == skill_lower
    ]

    def availability_rank(avail: str) -> int:
        return 0 if avail.lower() == "available" else 1

    sorted_workers = sorted(
        filtered,
        key=lambda w: (-w.rating, availability_rank(w.availability), -w.created_at),
    )

    top_workers = sorted_workers[:limit]
    return RecommendationResult(workers=top_workers)


@router.get("/{worker_id}", response_model=Worker)
def get_worker(worker_id: str) -> Worker:
    worker = fb_get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.put("/{worker_id}", response_model=Worker)
def update_worker(worker_id: str, update: WorkerUpdate) -> Worker:
    worker = fb_update_worker(worker_id, update)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.delete("/{worker_id}", status_code=204)
def delete_worker(worker_id: str) -> None:
    fb_delete_worker(worker_id)

