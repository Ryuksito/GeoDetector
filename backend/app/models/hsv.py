from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class HSVUpdate(BaseModel):
    lower_h: int
    lower_s: int
    lower_v: int
    upper_h: int
    upper_s: int
    upper_v: int

class HSV(BaseModel):
    lower_hsv: List[int]
    upper_hsv: List[int]