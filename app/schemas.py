from pydantic import BaseModel, Field
from datetime import datetime 
from typing import Optional

class AdultBase(BaseModel):
    name: str

class Adult(AdultBase):
    adult_id: int

    class Config:
        from_attributes = True

class DiaperChangeCreate(BaseModel):
    adult_id: int = Field(..., gt=0, description="ID på den som bytte blöja")
    change_type_id: int = Field(..., gt=0, description="1=Pee, 2=Poo, 3=Routine")
    accident: bool = False
    baby_id: int = 1 

class DiaperChangeRead(BaseModel):
    adult: str 
    change_type: str
    accident: bool = False
    
    class Config:
        from_attributes = True
