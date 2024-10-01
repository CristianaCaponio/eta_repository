
ITALIANO

Il calcolo degli eta si basa sull'api di di routing fornita da TomTom. 

Documentazione: https://developer.tomtom.com/routing-api/documentation/tomtom-maps/routing-service
Test: https://developer.tomtom.com/routing-api/api-explorer

Attualmente la request è una stringa caratterizzata dai seguenti parametri:
  1. stringa di coordinate con una struttura lat,long:lat,long:lat,long (ad esempio: "43.12345,16.12345:43.67891,16.67891:43.23456,16.23456)"
  2. routeType=fastest -> richiede il percorso più rapido
  3. ravelMode=car -> definisce il mezzo di trasporto utilizzato
  4. routeRepresentation=polyline -> rappresenta il percorso con una serie di coordinate lat/long. In questo caso si è deciso di rendere visibili solo le coordinate relative ai punti di partenza e di arrivo.
  5. departAt=now -> imposta l'orario di partenza al momento in cui viene inviata la request
  6. computeBestOrder=true -> riordina le coordinate inoltrate per rendere più rapido il percorso
  7. traffic=true -> considera eventuali ritardi dovuti al traffico nel calcolo degli ETA 
        

ENGLISH

The ETA calculation is based on the routing API provided by TomTom.

Documentation: https://developer.tomtom.com/routing-api/documentation/tomtom-maps/routing-service
Test: https://developer.tomtom.com/routing-api/api-explorer

Currently, the request is a string characterized by the following parameters:

  1. a string of coordinates in the format lat,long:lat,long:lat,lonh(e.g., "43.12345,16.12345:43.67891,16.67891:43.23456,16.23456").
  2. routeType=fastest -> requests the fastest route.
  3. travelMode=car -> defines the mode of transport.
  4. routeRepresentation=polyline -> represents the route as a series of lat/long coordinates. In this case, only the start and end point coordinates are made visible.
  5. departAt=now -> sets the departure time to the moment the request is sent.
  6. computeBestOrder=true -> reorders the submitted coordinates to optimize the route for speed.
  7. traffic=true -> takes into account traffic delays when calculating the ETA.