
ISTRUZIONI SULLO SVILUPPO 

l'applicazione allo stato attuale consente di calcolare l'ETA inserendo due o più percorsi. La response genera:
1) un JSON contenente un Summary generale in cui vengono indicati i tempi di percorrenza, la distanza in metri, l'indirizzo di partenza, l'indirizzo di arrivo, l'ora di partenza, l'ora di arrivo ed eventuali mutamenti legati al traffico;

2) dei summary secondari che forniscono le stesse informazioni sui vari percorsi;

3) un piccolo riepilogo contenente la modalità di trasporto e gli start/endpointIndex che, però, potrebbero anche essere tolti modificando il json di risposta nel file eta_calculation_service. 

L'ETA calcolata e l'orario di arrivo sono già comprensivi dei ritardi indicati dai cap presenti nel file zip_code.json. Per testare il corretto funzionamento dei ritardi (ho fatto un paio di test, ma non mi sono divertita a rompere tutto purtroppo) conviene utilizzare contemporaneramente l'api su swagger/postman e la sezione "API Explorer" di TomTom (https://developer.tomtom.com/routing-api/api-explorer) di cui ti passo tutte le credenziali. Il servizio utilizzato è ROUTING API (https://developer.tomtom.com/routing-api/documentation/tomtom-maps/product-information/introduction)

mail: cristiana.caponio@ngs-sensors.it
password: mXPf^k$*6t]709k

NOTA: nella sezione "location" di TOMTOM vanno inserite solo le coordinate seguendo questa struttura 41.1044997,16.8630293:41.1040066,16.864305:41.1030466. Trovi gli indirizzi trasformati in coordinate nei logger, ti basta solo lasciare cinque cifre dopo ogni virgola perchè altrimenti sul sito non le prende. 

in input è attualmente inserito un JSON con questi dati:

{
  "location": [
    {
      "address": string,
      "city": string,
      "district": string,
      "house_number": string,
      "zip_code": string
    }
    
  ],
  "routeType": string, (le possibilità sono fastest, shortest, eco e thrilling )
  "travelMode": "string", (le possibilità sono: pedestrian, car, truck, van,taxi, bus, bicycle, motorcycle, van)
  "departAt": "2024-08-23T10:00:00", (l'ho fatta in formato stringa)
  "routeRepresentation": "string" (bisogna mettere per forza summaryOnly perchè altrimenti l'elaborazione diventa inutilmente complessa)
}
NOTA 1: se zip_code o house_number sono errati/non esistono non viene generato alcun errore, mentre per address,city e district si
NOTA 2: non ho inserito l'opzione sul traffico perchè il valore è settato "true" di default
NOTA 3: gli indirizzi da inserire sono sempre minimo 2

COSE DA FARE:
- inserire la funzionalità che consente di inviare mail quando manca un certo tempo dalla destinazione. Ho pensato di usare smtplib di python (https://realpython.com/python-send-email/)
- inserire la possibilità di far segnare ai corrieri "now" come ora di partenza, visto che lasciare departAt privo di valore mi genera errore
- eventualmente settare sempre "summaryOnly" su routeType 