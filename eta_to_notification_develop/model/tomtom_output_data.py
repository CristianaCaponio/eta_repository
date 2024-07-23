from pydantic import BaseModel
from typing import List

"""model to create the TomTom output json"""

class RouteSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    departureTime: str
    arrivalTime: str

class Point(BaseModel):
    latitude: float
    longitude: float

class LegSummary(BaseModel):
    lengthInMeters: int
    travelTimeInSeconds: int
    trafficDelayInSeconds: int
    trafficLengthInMeters: int
    departureTime: str
    arrivalTime: str

class Leg(BaseModel):
    summary: LegSummary
    points: List[Point]

class Section(BaseModel):
    startPointIndex: int
    endPointIndex: int
    sectionType: str
    travelMode: str

class Route(BaseModel):
    summary: RouteSummary
    legs: List[Leg]
    sections: List[Section]

class TomTomResponse(BaseModel):
    formatVersion: str
    routes: List[Route]