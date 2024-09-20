from pydantic import BaseModel
from typing import List, Optional
from model.geopy_input_data import GeopyInputData
"""classes for the first input"""


class InitialSummary(BaseModel):
    startAddress: str
    startLatitude: float
    startLongitude: float
    endAddress: str
    endLatitude: float
    endLongitude: float


class InitialStopSummary(BaseModel):
    departureAddress: str
    departureLatitude: float
    departureLongitude: float
    arrivalAddress: str
    arrivalLatitude: float
    arrivalLongitude: float


class InitialTravelData(BaseModel):
    summary: InitialSummary
    stops: List[InitialStopSummary]


"""classes that populate the database"""


class Summary(BaseModel):
    travelMode: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    startAddress: GeopyInputData
    startLatitude: Optional[float]
    startLongitude: Optional[float]
    endAddress:  GeopyInputData
    endLatitude: float
    endLongitude: float
    departureTime: Optional[str] = ""
    arrivalTime: Optional[str] = ""


class StopSummary(BaseModel):
    gsin: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    departureAddress: GeopyInputData
    departureLatitude: Optional[float]
    departureLongitude: Optional[float]
    arrivalAddress: GeopyInputData
    arrivalLatitude: Optional[float]
    arrivalLongitude: Optional[float]
    departureTime: Optional[str] = ""
    arrivalTime: Optional[str] = ""
    delivered: Optional[bool] = False


class TravelData(BaseModel):
    personal_id: str
    summary: Summary
    stops: List[StopSummary]
