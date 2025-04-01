from smsapi.client import SmsApiComClient

api_token = '______________'
client = SmsApiComClient(access_token=api_token)

send_results = client.sms.send(to="+______", message="questo è un messaggio di prova")

for result in send_results:
    print(result.id, result.points, result.error)