
from kavenegar import KavenegarAPI, APIException, HTTPException


def send_sms(receiver, template, token, token2, token3):
    try:
        api = KavenegarAPI('5550477A4E46442F34425A4E533169377077355544464C546572473367745279474D617379774F344A46673D')
        params = {
            'receptor': receiver,
            'template': template,
            'token': token,
            'token2': token2,
            'token3': token3,
            'type': 'sms',  # sms vs call
        }
        response = api.verify_lookup(params)
        return 200
    except APIException as e:
        return 404
    except HTTPException as e:
        return 404
