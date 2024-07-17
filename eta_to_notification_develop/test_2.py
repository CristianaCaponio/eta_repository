from io import StringIO

shopping_list = [("arance","melone"),("pasta","patate"),("gelato","pizza surgelata"),("pollo","spezie")]

res = str(shopping_list)
sentence = StringIO()
sentence.write(res[0])

for shopping_item in res[1:]:
    sentence.write(":" + shopping_item)

print(sentence.getvalue())






# import requests
# import urllib.parse as urlparse
# import os

# API_KEY: os.getenv("TOMTOM_API_KEY")

# # Route parameters
# start = "37.77493,-122.419415"               # San Francisco
# end = "34.052234,-118.243685"                # Los Angeles
# routeType = "fastest"                        # Fastest route
# traffic = "true"                             # To include Traffic information
# travelMode = "truck"                         # Travel by truck
# avoid = "unpavedRoads"                       # Avoid unpaved roads
# departAt = "2021-10-20T10:00:00"             # Departure date and time
# vehicleCommercial = "true"                   # Commercial vehicle 
# key = "API_KEY"                             # API Key

# # Building the request URL
# baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/",

# requestParams = (
#     urlparse.quote(start) + ":" + urlparse.quote(end) 
#     + "/json?routeType=" + routeType
#     + "&traffic=" + traffic
#     + "&travelMode=" + travelMode
#     + "&avoid=" + avoid 
#     + "&vehicleCommercial=" + vehicleCommercial
#     + "&departAt=" + urlparse.quote(departAt))

# requestUrl = baseUrl + requestParams + "&key=" + key

# print("Request URL: " + requestUrl + "\n")

# # Sending the request
# response = requests.get(requestUrl)

# if(response.status_code == 200):
#     # Get response's JSON
#     jsonResult = response.json()

#     # Read summary of the first route
#     routeSummary = jsonResult['routes'][0]['summary']
    
#     # Read ETA
#     eta = routeSummary['arrivalTime']

#     # Read travel time and convert it to hours
#     travelTime = routeSummary['travelTimeInSeconds'] / 3600
    
#     # Print results
#     print(f"Depart at: {departAt},\tETA: {eta},\tTravel time: {travelTime:.2f}h")