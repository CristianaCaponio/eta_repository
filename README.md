ITALIANO

Descrizione generale del sistema

Questo sistema è progettato per gestire il tracciamento delle consegne e aggiornare i tempi di arrivo stimati (ETA) per ogni fermata del corriere. Il sistema si basa sul servizio di routing fornito da TomTom, a cui si affiancano modelli di dati strutturati che rappresentano informazioni sui viaggi, gli indirizzi, le fermate e le consegne.

Qui il link alla documentazione e alla piattaforma di test di TomTom
https://developer.tomtom.com/routing-api/documentation/tomtom-maps/product-information/introduction#routing-api


I singoli servizi
_________

    1./eta_calculator/upload_route_file/ Create Upload File:
        Il servizio riceve in input un csv che deve essere necessariamente nominato nella seguente modalità: yyyy_mm_dd_idNumber (esempio: 2024_12_20_id001). Il file
        contiene il percorso giornaliero con le seguenti informazioni, rinvenibili all'interno del model "Delivery":
        - gsin
        - address -> indirizzo senza cap e numero civico
        - city -> città
        - dictrict -> provincia
        - house_number -> numero civico
        - zip_code -> cap
        - telephone_number -> numero di telefono (in formato 39XXXXXXXXXX)

       Il contenuto del csv viene elaborato con la chiamata a TomTom, a seguito della quale viene restituito un csv con l'indirizzo di partenza come punto iniziale, contrassegnato dalla dicitura "start/ending point", ed  il percorso ottimizzato con l'orario stimato di arrivo per ciascuna tappa (si presuppone che l'orario di parenza coincida sempre con quello della chiamata a TomTom), calcolato anche sulla base dei CAP inseriti nella lista "zip_code.json".
       Le informazioni elaborate sono inserite nel database nel modello definito in "TravelData" e come ginc viene assegnato l'idNumber del file csv.
       Gli orari salvati in database sono in formato UTC+0

       Nota: il punto di partenza coincide anche con il punto di arrivo finale, per cui il sistema ottimizza il tragitto facendo in modo che il veicolo ritorni al punto di partenza.

    2./eta_calculator/get_route/ Get Route Object By Ginc
        Il servizio permette di visualizzare un percorso salvato nel database prendendo in input il suo ginc

    3./eta_calculator/route_delete/ Delete Trace
        Il servizio permette di cancellare un intero percorso prendendo in input il suo ginc

    4./eta calculator/route_update/ Route Update
        Il servizio prende in input le seguenti informazioni, rinvenibili all'interno del model "Delivery"
        - ginc
        - gsin
        - delivery_time -> è già impostato all'orario della richiesta ed è in formato UTC
        A seguito della chiamata, la fermata viene contrassegnata con delivered=True e viene nuovamente chiamato il servizio di TomTom che, senza ottimizzare il percorso,  provvede ad aggiornare gli ETA.
        Il database viene aggiornato con i dati del nuovo ricalcolo e con la fermata contrassegnata spostata in una lista chiamata delivered_stops.


ENGLISH

General Description of the System

This system is designed to manage delivery tracking and update the estimated time of arrival (ETA) for each stop in a delivery journey. It relies on the routing service provided by TomTom, supported by structured data models representing information about trips, addresses, stops, and deliveries.

TomTom Routing API Documentation and Test Platform:
https://developer.tomtom.com/routing-api/documentation/tomtom-maps/product-information/introduction#routing-api

Services


      1. /eta_calculator/upload_route_file/ Create Upload File:
            This service processes a CSV file, which must be named using the following format: yyyy_mm_dd_idNumber (e.g., 2024_11_20_id001). The file contains the daily route with the following details, found in the "Delivery" model:

            -gsin
            -address -> address without ZIP code or house number
            -city
            -district
            -house_number
            -zip_code
            -telephone_number -> phone number in the format 39XXXXXXXXXX

            The CSV content is processed through a call to TomTom, which returns a CSV file with the starting address as the initial point, marked with the label "start/ending point," and the optimized route with the estimated arrival time for each stop (it is assumed that the departure time always coincides with the time of the call to TomTom), calculated based on the ZIP codes provided in the "zip_code.json" list.

            The processed information is stored in the database in the model defined in "TravelData," and the CSV file's idNumber is assigned as the ginc.
            The times saved in the database are in UTC+0 format.

            Note: The starting point also coincides with the final endpoint, so the route is optimized to ensure the vehicle returns to the starting point.

      2. /eta_calculator/get_route/ Get Route Object By Ginc
            This service allows retrieving a saved route from the database by providing its ginc as input.

      3. /eta_calculator/route_delete/ Delete Trace
          This service deletes an entire route from the database using its ginc.

      4. /eta_calculator/route_update/ Route Update
          This service accepts the following details from the "Delivery" model:
          -ginc
          -gsin
          -delivery_time -> pre-set to the request time in UTC

        Upon invocation:
            The stop is marked with delivered=True.
            TomTom is called again (without route optimization) to update the ETAs.
            The database is updated with the recalculated data, and the completed stop is moved to a list named delivered_stops.

