from pydantic import BaseModel
from typing import List, Optional
from model.geopy_input_data import GeopyInputData
"""classes for the first input"""



"""classes that populate the database"""


class Summary(BaseModel):
    travelMode: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    startAddress: GeopyInputData
    startLatitude: float = None
    startLongitude: float = None
    endAddress:  GeopyInputData
    endLatitude: float = None
    endLongitude: float = None
    departureTime: Optional[str] = ""
    arrivalTime: Optional[str] = ""


class StopSummary(BaseModel):
    gsin: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    departureAddress: GeopyInputData
    departureLatitude:float = None
    departureLongitude: float = None
    arrivalAddress: GeopyInputData
    arrivalLatitude: float = None
    arrivalLongitude: float = None
    departureTime: Optional[str] = ""
    arrivalTime: Optional[str] = ""
    delivered: Optional[bool] = False


class TravelData(BaseModel):
    personal_id: str
    summary: Summary
    stops: List[StopSummary]
