from fastapi import APIRouter, HTTPException
from app import crud, schemas

router = APIRouter()


@router.post("/changes/", status_code=201)
def add_change(change: schemas.DiaperChangeCreate):
    result = crud.create_diaper_change(change)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/changes/", response_model=list[schemas.DiaperChangeRead])
def read_recent_changes(limit: int = 10):
    return crud.get_recent_changes(limit=limit)


@router.post("/sleep/", status_code=201)
def add_sleep(sleep: schemas.SleepCreate):
    result = crud.create_sleep_session(sleep)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/sleep/", response_model=list[schemas.SleepRead])
def read_sleep(hours: int = 24):
    return crud.get_sleep_sessions(hours=hours)


@router.post("/food/", status_code=201)
def add_food(food: schemas.FoodCreate):
    result = crud.create_food_intake(food)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/food/", response_model=list[schemas.FoodRead])
def read_food(hours: int = 24):
    return crud.get_food_intake(hours=hours)
