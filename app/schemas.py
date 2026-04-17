from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class AdultBase(BaseModel):
    name: str

class Adult(AdultBase):
    adult_id: int

    class Config:
        from_attributes = True


class DiaperChangeCreate(BaseModel):
    adult_id: int = Field(..., gt=0)
    change_type_id: int = Field(..., gt=0, description="1=Pee, 2=Poo, 3=Routine")
    accident: bool = False
    baby_id: int = 1

class DiaperChangeRead(BaseModel):
    adult: str
    change_type: str
    accident: bool = False
    change_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SleepCreate(BaseModel):
    adult_id: int = Field(..., gt=0)
    baby_id: int = 1
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None

class SleepRead(BaseModel):
    adult: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class FoodCreate(BaseModel):
    adult_id: int = Field(..., gt=0)
    baby_id: int = 1
    food_type: Literal["breast", "bottle", "solid"]
    amount_ml: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None

class FoodRead(BaseModel):
    adult: str
    food_type: str
    amount_ml: Optional[int] = None
    logged_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
