from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from model.delivery import Address


class Summary(BaseModel):
    '''This class contains the summary of the travel, including start and end addresses, travel times,
    and traffic information.'''
    travelMode: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    startAddress: Address
    startLatitude: float = None
    startLongitude: float = None
    endAddress:  Address
    endLatitude: float = None
    endLongitude: float = None
    departureTime: Optional[datetime] = None
    arrivalTime: Optional[datetime] = None


class StopSummary(BaseModel):
    '''This class contains information about each stop during the journey, including departure and arrival addresses, times,
    and delivery status.'''

    gsin: Optional[str] = ""
    lengthInMeters: Optional[int] = 0
    travelTimeInSeconds: Optional[int] = 0
    trafficDelayInSeconds: Optional[int] = 0
    trafficLengthInMeters: Optional[int] = 0
    departureAddress: Address
    departureLatitude: float = None
    departureLongitude: float = None
    arrivalAddress: Address
    arrivalLatitude: float = None
    arrivalLongitude: float = None
    departureTime: Optional[datetime] = None
    arrivalTime: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivered: Optional[bool] = False
    message_sent: Optional[bool] = False
    message_report: Optional[str] = ""


class TravelData(BaseModel):
    '''This class recalls the Summary class and contains a list of stops. It is updated by every function and is stored inside the db'''
    personal_id: str
    ginc: str
    summary: Summary
    stops: List[StopSummary]
    delivered_stops: List[StopSummary]
