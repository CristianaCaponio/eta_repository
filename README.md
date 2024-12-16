
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

    1./follow_track_api/upload_route_file/ Create Upload File:
        Il servizio riceve in input un csv che deve essere necessariamente nominato nella seguente modalità: yyyy_mm_dd_idNumber (esempio: 2024_12_20_id001). Il file
        contiene il percorso giornaliero con le seguenti informazioni, rinvenibili all'interno del model "Delivery":
        - gsin 
        - address -> indirizzo senza cap e numero civico
        - city -> città
        - dictrict -> provincia
        - house_number -> numero civico
        - zip_code -> cap
        - telephone_number -> numero di telefono (in formato 39XXXXXXXXXX)
       
       Il contenuto del csv viene elaborato con la chiamata a TomTom, a seguito della quale viene restituito un csv con il percorso ottimizzato assieme all'orario stimato di arrivo per ciascuna tappa (si presuppone che l'orario di parenza coincida sempre con quello della chiamata a TomTom). A tutti i destinatari viene inviato un sms con l'ora stimata di arrivo e se l'orario di ogni tappa è inferiore di 30 minuti rispetto a quello di partenza,  ai destinarari viene inviato un ulteriore sms contenente un range di orario per la consegna effettiva. Tale risposta è contenuta nel modello "Response"
       Le informazioni elaborate sono inserite nel database nel modello definito in "TravelData" e come ginc viene assegnato l'idNumber del file csv.
       Gli orari salvati in database sono in formato UTC+0
       
    2./follow_track_api/get_route/ Get Route Object By Ginc
        Il servizio permette di visuaizzare un percorso salvato nel database prendendo in input il suo ginc
    
    3./follow_track_api/route_delete/ Delete Trace
        Il servizio permette di cancellare un intero percorso prendendo in input il suo ginc

    4./follow_track_api/route_update/ Route Update  - UTILIZZABILE PER I TEST
        Il servizio prende in input le seguenti informazioni, rinvenibili all'interno del model "Delivery"
        - ginc
        - gsin
        - delivery_time -> è già impostato all'orario della richiesta ed è in formato UTC
        A seguito della chiamata, la fermata viene contrassegnata con delivered=True ed al destinatario viene inviato un messaggio di avvenuta consegna del pacco.  
        Viene nuovamente chiamato il servizio di TomTom che, senza ottimizzare il percorso,  provvede ad aggiornare gli eta e ad inviare le notifihe ai destinatari se l' orario di arrivo è inferiore di un'ora rispetto alla partenza. La risposta, contenuta nel modello "Response" contiene gli aggiornamenti del delivered=True,della chiamata a TomTom e dell'inoltro dei messaggi.
        Il database viene aggiornato con i dati del nuovo ricalcolo e con la fermata contrassegnata spostata in una lista chiamata delivered_stops. 

    5./follow_track_api/tracker_update/ Route Update
        Il servizio consente di aggiornare lo stato di consegna di una specifica tappa del percorso e di ricalcolare i dettagli della rotta.
        Si identifica la rotta corrente recuperando dal database i seguenti dati: 
        -lat
        -long
        -time
        Quest'ulimo, in particolare, è in formato stringa perchè il tracker inoltra l'orario sotto forma di stringa avente una struttura simile a quella di un datetime (ad esempio 2024-12-16T14:49:57.000+00:00).
        
        Con questi dati si verifica  che il tracker sia:
        - entro 10 metri dalla posizione della tappa non ancora consegnata.
        - all'interno di un range temporale di ±10 minuti rispetto all'orario programmato per la consegna.

        Se entrambi i requisiti sono rispettati, la tappa viene contrassegnata come "delivered". E' possibile anche inviare un SMS al destinatatio per confermare
        l'avvenuta consegna, ma attualmente la funzione è commentata.
        Inoltre il sistema aggiorna l'intera rotta con le tappe rimanenti e ricalcola i tempi stimati di arrivo (ETA) applicando eventuali ritardi basati sui CAP presenti nel file zip_code.json.

        La rotta aggiornata viene salvata nel database, con gli orari in formato UTC+0

        Se i due requisiti di tempo e luogo relativi al tracker non sono rispettati, il sistema restituisce il messaggio: "no proof of delivery".

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

      1. /follow_track_api/upload_route_file/ Create Upload File:
            This service processes a CSV file, which must be named using the following format: yyyy_mm_dd_idNumber (e.g., 2024_11_20_id001). The file contains the daily route with the following details, found in the "Delivery" model:

            -gsin
            -address -> address without ZIP code or house number
            -city 
            -district 
            -house_number 
            -zip_code 
            -telephone_number -> phone number in the format 39XXXXXXXXXX

            The content of the CSV is processed using a call to TomTom, which returns an optimized route along with the estimated arrival time (ETA) for each stop. The departure time is assumed to match the time of the call to TomTom.

            An SMS with the estimated arrival time is sent to all recipients. If the ETA for any stop is within 30 minutes of the departure time, an additional SMS with a delivery time range is sent to the recipients. The response to this operation is contained in the "Response" model.

            Processed information is stored in the database in the "TravelData" model, with the idNumber of the CSV file assigned as the ginc.
            Note: All saved times are in UTC+0 format.

      2. /follow_track_api/get_route/ Get Route Object By Ginc
            This service allows retrieving a saved route from the database by providing its ginc as input.

      3. /follow_track_api/route_delete/ Delete Trace
          This service deletes an entire route from the database using its ginc.

      4. /follow_track_api/route_update/ Route Update - TEST MODE
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

    5. /follow_track_api/tracker_update/ Route Update
        This service updates the delivery status of a specific stop in the route and recalculates route details.

        The current route is identified by retrieving the following data from the database:
            -lat
            -long
            -time

        The time field, in particular, is provided as a string, as the tracker sends it in a datetime-like format (e.g., 2024-12-16T14:49:57.000+00:00).

        The service verifies that the tracker is:

            Within 10 meters of the undelivered stop's location.
            Within a ±10-minute time range of the scheduled delivery time.

        If both conditions are met:

            The stop is marked as delivered.
            (Optional) An SMS can be sent to the recipient to confirm delivery, though this functionality is currently commented out.
            The route is updated to reflect remaining stops, and ETAs are recalculated with any delays applied based on ZIP codes from the zip_code.json file.

        The updated route is saved in the database, with all times in UTC+0 format.

        If the tracker fails the time or location validation, the system returns the message: "no proof of delivery".