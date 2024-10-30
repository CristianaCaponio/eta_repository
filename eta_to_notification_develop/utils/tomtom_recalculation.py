import requests
from model.travel_data import TravelData
from datetime import datetime
from loguru import logger
import os

"""questo è un test. Sto lasciando i nomi dei metodi uguali a quelli della classe TomTom per fare il confronto e capire come e se ottimizzare"""


class TomTomRecalculation:
    """in this class are stored all the functions related to TomTom and the population of TravelData with the ETAs 
    and information provided by tomTom routing api after the first request"""

    @staticmethod
    def order_travel_data(travel_data: TravelData) -> TravelData:
        """this function takes in input a list of strings (the coordinates in string format) and returns a TravelData object.
        I   t recalls all the following functions to create the coordinates string with the format requested by TomTom url, to make the request to TomTom
            and to parse the response in order to obtain a TravelData object populated with all TomTom informations and eta calculations"""

        tomtom_url = TomTomRecalculation.create_request_string(travel_data)
        json_response = TomTomRecalculation.tomtom_request(tomtom_url)
        ordered_travel_data = TomTomRecalculation.parse_tomtom_response(
            json_response, travel_data)
        return ordered_travel_data

    @staticmethod
    def create_request_string(travel_data: TravelData) -> str:        
        """
        Creates a request string for TomTom API based on a list of stops. If 'delivered' is True, only the 
        departure coordinates of the first undelivered stop and the arrival coordinates of undelivered stops are used.
        """

        departure_coordinates = None
        arrival_coordinates = []

        for single_stop in travel_data.stops:
            #logger.info(f"i delivered fuori dall'if è {single_stop.delivered}")

            #logger.info(f"il singolo stop è {single_stop}")
            if  not single_stop.delivered: #== False:               
                
                if departure_coordinates is None:
                    departure_coordinates = [single_stop.departureLatitude, single_stop.departureLongitude] 
                    logger.info(f"il departure_coordinate è {departure_coordinates}")
                                 
                #logger.info(f"i delivered dentro l'if è {single_stop.delivered}") 
                arrival_coordinates.append([single_stop.arrivalLatitude, single_stop.arrivalLongitude])
            
                
        coordinate_list = [departure_coordinates] + arrival_coordinates
        coordinate_str = ":".join([f"{coord[0]},{coord[1]}" for coord in coordinate_list])

        return (
            coordinate_str
            + "/json?routeType=fastest"
            + "&travelMode=car"
            + "&routeRepresentation=summaryOnly"
            + "&departAt=now"
            + "&computeBestOrder=false"
            + "&traffic=true"
        )

    @staticmethod
    def tomtom_request(request_params: str) -> TravelData:
        """this function is used to make the request to TomTom and returns a json with the TomTom format"""

        baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/"
        API_KEY = os.getenv("TOMTOM_API_KEY")
        if not API_KEY:
            raise ValueError("TOMTOM_API_KEY environment variable is not set.")

        requestUrl = baseUrl + request_params + "&key=" + API_KEY
        logger.info("Request URL: " + requestUrl + "\n")

        response = requests.get(requestUrl)
        # logger.info(response)
        response.raise_for_status()

        if response.status_code == 200:
            jsonResult = response.json()
            return jsonResult
        else:
            return None

    @staticmethod
    def parse_tomtom_response(json_response: dict, travel_data: TravelData) -> TravelData:
        """This function parses the response provided by TomTom and modifies the existing TravelData object with its data."""
              
        tomtom_length_in_meters = json_response["routes"][0]["summary"]["lengthInMeters"]
        tomtom_travel_time_in_seconds = json_response["routes"][0]["summary"]["travelTimeInSeconds"]
        tomtom_traffic_delay_in_seconds = json_response["routes"][0]["summary"]["trafficDelayInSeconds"]
        tomtom_traffic_length_in_meters = json_response["routes"][0]["summary"]["trafficLengthInMeters"]
        start_time_iso = datetime.fromisoformat(json_response["routes"][0]["summary"]["departureTime"])       
        end_time_iso = datetime.fromisoformat(json_response["routes"][0]["summary"]["arrivalTime"])                 

        travel_data.summary.lengthInMeters = tomtom_length_in_meters
        travel_data.summary.travelTimeInSeconds = tomtom_travel_time_in_seconds
        travel_data.summary.trafficDelayInSeconds = tomtom_traffic_delay_in_seconds
        travel_data.summary.trafficLengthInMeters = tomtom_traffic_length_in_meters
        travel_data.summary.departureTime = start_time_iso
        logger.info(f"il departure time del summary è { travel_data.summary.departureTime }")
        travel_data.summary.arrivalTime = end_time_iso
        logger.info(f"l'arrival time del summary è { travel_data.summary.arrivalTime }")

        for leg_index, leg_data in enumerate(json_response["routes"][0]["legs"]):
            stop = travel_data.stops[leg_index]               
                     

            stop.lengthInMeters = leg_data["summary"]["lengthInMeters"]
            stop.travelTimeInSeconds = leg_data["summary"]["travelTimeInSeconds"]
            stop.trafficDelayInSeconds = leg_data["summary"]["trafficDelayInSeconds"]
            stop.trafficLengthInMeters = leg_data["summary"]["trafficLengthInMeters"]
            stop.departureTime = datetime.fromisoformat(leg_data["summary"]["departureTime"])
            logger.info(f"il departure time dello stop è {stop.departureTime}")
            stop.arrivalTime = datetime.fromisoformat(leg_data["summary"]["arrivalTime"])
            logger.info(f"l'arrival time dello stop è {stop.arrivalTime}")

        undelivered_stops = [stop for stop in travel_data.stops if not stop.delivered]       
        travel_data.stops = undelivered_stops   

        if undelivered_stops:  
            travel_data.summary.startAddress = travel_data.stops[0].departureAddress
            travel_data.summary.endAddress = travel_data.stops[-1].arrivalAddress 

        else:
            travel_data.summary.startAddress = None
            travel_data.summary.endAddress = None
    
        #logger.info(f"i travel_data usciti dal parse_tomtom_response sono: {travel_data}")
        return travel_data