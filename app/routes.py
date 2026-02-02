from fastapi import APIRouter, HTTPException
from typing import List
from app import crud, schemas

router = APIRouter()

@router.post("/changes/", status_code=201)
def add_change(change: schemas.DiaperChangeCreate):
    result = crud.create_diaper_change(change)
    
    if result ["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/changes/", response_model=list[schemas.DiaperChangeRead])
def read_recent_changes(limit: int = 10):
    changes = crud.get_recent_changes(limit=limit)
    return changes 
