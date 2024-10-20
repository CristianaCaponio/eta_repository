from smsapi.client import SmsApiComClient

api_token = 'oOVBn57zBhvOlaFVPBQWahNC55zyxs8YInPr1MJD'
client = SmsApiComClient(access_token=api_token)

send_results = client.sms.send(to="+393398571511", message="questo è un messaggio di prova")

for result in send_results:
    print(result.id, result.points, result.error)