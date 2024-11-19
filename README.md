


ITALIANO

Descrizione generale del sistema

Questo sistema è progettato per gestire il tracciamento delle consegne, inviare notifiche di arrivo/avvenuta consegna tramite SMS e aggiornare i tempi di arrivo stimati (ETA) per ogni stop di un viaggio di consegna. Il sistema si basa sul servizio di routing fornito da TomTom e sul servizio di inoltro sms automatici fornito da SmsApi, a cui si affiancano modelli di dati strutturati che rappresentano informazioni sui viaggi, gli indirizzi, le fermate e le consegne.

Qui il link alla documentazione e alla piattaforma di test di TomTom
https://developer.tomtom.com/routing-api/documentation/tomtom-maps/product-information/introduction#routing-api

Qui il link alla documentazione di SmsApi
https://www.smsapi.com/docs/#sms-api-documentation-1-introduction
https://github.com/smsapi/smsapi-python-client/tree/master/examples


I singoli servizi

Qui il link alla piattaforma
http://localhost:8010/docs

    1.Create Upload File:
        Il servizio riceve in input un csv che deve essere necessariamente nominato nella seguente modalità: yyyy_mm_dd_idNumber (esempio: 2024_11_20_id001). Il file
        contiene il percorso giornaliero con le seguenti informazioni, rinvenibili all'interno del model "Delivery":
        - gsin 
        - address -> indirizzo senza cap e numero civico
        - city -> città
        - dictrict -> provincia
        - house_number -> numero civico
        - zip_code -> cap
        - telephone_number -> numero di telefono (in formato +39XXXXXXXXXX)
       
       Il contenuto del csv viene elaborato con la chiamata a TomTom, a seguito della quale viene restituito un percorso ottimizzato assieme all'orario stimato di arrivo per ciascuna tappa (si presuppone che l'orario di parenza coincida sempre con quello della chiamata a TomTom). Se l'orario di ogni tappa è inferiore a quello di partenza di un'ora,  ai destinarari viene inviato un sms contenente l'orario stimato di consegna. Tale risposta è contenuta nel modello "Response"
       Le informazioni elaborate sono inserite nel database nel modello definito in "TravelData" e come ginc viene assegnato l'idNumber del file csv.
       Nota: gli orari sono in formato UTC
       
    2.Get Route Object By Ginc
        Il servizio permette di visuaizzare un percorso salvato nel database prendendo in input il suo ginc
    
    3.Delete Trace
        Il servizio permette di cancellare un intero percorso prendendo in input il suo ginc

    4.Route Update
        Il servizio prende in input le seguenti informazioni, rinvenibili all'interno del model "Delivery"
        - ginc
        - gsin
        - delivery_time -> è già impostato all'orario della richiesta ed è in formato UTC
        A seguito della chiamata, la fermata viene contrassegnata con delivered=True ed al destinatario viene inviato un messaggio di avvenuta consegna del pacco.  
        Viene nuovamente chiamato il servizio di TomTom che, senza ottimizzare il percorso,  provvede ad aggiornare gli eta e ad inviare le notifihe ai destinatari se l' orario di arrivo è inferiore di un'ora rispetto alla partenza. La risposta, contenuta nel modello "Response" contiene gli aggiornamenti del delivered=True,della chiamata a TomTom e dell'inoltro dei messaggi.
        Il database viene aggiornato con i dati del nuovo ricalcolo e con la fermata contrassegnata spostata in una lista chiamata delivered_stops. 


ENGLISH

General Description of the System

This system is designed to manage delivery tracking, send arrival/delivery notifications via SMS, and update the estimated time of arrival (ETA) for each stop in a delivery journey. It relies on the routing service provided by TomTom and the automated SMS forwarding service from SmsApi, supported by structured data models representing information about trips, addresses, stops, and deliveries.

TomTom Routing API Documentation and Test Platform:
https://developer.tomtom.com/routing-api/documentation/tomtom-maps/product-information/introduction#routing-api

SmsApi documentation
https://www.smsapi.com/docs/#sms-api-documentation-1-introduction
https://github.com/smsapi/smsapi-python-client/tree/master/examples


Services

Platform Link:
http://localhost:8010/docs

      1. Create Upload File
          This service processes a CSV file, which must be named using the following format: yyyy_mm_dd_idNumber (e.g., 2024_11_20_id001). The file contains the daily route with the following details, found in the "Delivery" model:

          -gsin
          -address -> address without ZIP code or house number
          -city 
          -district 
          -house_number 
          -zip_code 
          -telephone_number -> phone number in the format +39XXXXXXXXXX

          The CSV content is processed through a TomTom API call, returning an optimized route along with an estimated arrival time for each stop. The departure time is assumed to match the time of the TomTom call. If the ETA at any stop is less than an hour from the departure time, recipients receive an SMS with the estimated delivery time. The response is stored in the "Response" model.

          The processed information is stored in the database under the "TravelData" model, with the CSV's idNumber assigned as the ginc.
          Note: Times are in UTC.

      2. Get Route Object By Ginc
          This service retrieves a saved route from the database using its ginc.

      3. Delete Trace
          This service deletes an entire route from the database using its ginc.

      4. Route Update
          This service accepts the following details from the "Delivery" model:

          -ginc
          -gsin
          -delivery_time -> pre-set to the request time in UTC

        Upon invocation:
            The stop is marked with delivered=True.
            A delivery confirmation SMS is sent to the recipient.
            TomTom is called again (without route optimization) to update the ETAs. If the arrival time is less than an hour from departure, SMS notifications are sent to the recipients.
            The response, stored in the "Response" model, includes updates for delivered=True, the TomTom call, and the forwarded messages.
            The database is updated with the recalculated data, and the completed stop is moved to a list named delivered_stops.