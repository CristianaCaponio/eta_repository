from pydantic import BaseModel
from typing import List, Optional

"""model to create the TomTom output json"""

class RouteSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    startAddress: Optional[str] 
    endAddress: Optional[str] 
    departureTime: str
    arrivalTime: str

class LegSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    departureAddress: Optional[str] 
    arrivalAddress: Optional[str]  
    departureTime: str
    arrivalTime: str

class Leg(BaseModel):
    summary: LegSummary
    
class Route(BaseModel):
    summary: RouteSummary
    legs: List[Leg]
   
class TomTomResponse(BaseModel):
    formatVersion: str
    routes: List[Route]