
from model.tracker import TrackerMessage
from loguru import logger
import json
import os
from typing import Dict
import requests
from requests.models import Response


def from_object_to_json(informations: TrackerMessage):
    """
    Funcion to convert a instance into a json
    Input:
        instance
    Output: 
        Json
    """

    information_dict = informations.dict()
    information_json = json.dumps(
        information_dict, indent=4, sort_keys=True, default=str)
    logger.debug(information_json)
    return information_json


def send_message(message: Dict) -> Response:
    """
    Function to send a message.
    """
    try:
        logger.debug("Sending POST request.")
        url = "http://0.0.0.0:8010/follow_track_api/tracker_update/"
        # payload = dumps(message)
        response = requests.post(url=url, data=message, headers={
                                 "Content-Type": "application/json"})
        logger.debug(f"Response: {response.content}")
        return response
    except ConnectionError as e:
        logger.error(f'Connection Error: {e}')
