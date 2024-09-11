from pydantic import BaseModel
from typing import List

"""model to create the TomTom output json"""

class RouteSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    startAddress: str
    endAddress: str 
    departureTime: str
    arrivalTime: str

class LegSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    departureAddress: str 
    arrivalAddress: str 
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