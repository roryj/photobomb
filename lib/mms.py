#!/usr/bin/env python3

# Download the helper library from https://www.twilio.com/docs/python/install
import os
#from twilio.rest import Client
import requests 

simple_sms_auth_token = os.environ['SIMPLE_SMS_TOKEN']

"""
tw_account_sid = os.environ['TWILIO_ACCOUNT_SID']
tw_auth_token = os.environ['TWILIO_AUTH_TOKEN']
tw_client = None

phlo_auth_id = os.environ['PLIVO_AUTH_ID']
phlo_auth_token = os.environ['PLIVO_AUTH_TOKEN']
phlo_id = os.environ['PLIVO_ID']
phlo = None
"""

def send_text(number, mms_content, preview_image):
    send_simple_sms_text(number, mms_content, preview_image)

def send_simple_sms_text(number, mms_content, preview_image):
    endpoint = "https://api-app2.simpletexting.com/v2/api/messages"
    payload = {
        "contactPhone": number,
        "mode": "MMS_PREFERRED",
        "text": mms_content,
        "fallbackText": "[url=%%fallback_link%%]",
        "mediaItems": [preview_image]
    }
    headers = {"Authorization": f"Bearer {simple_sms_auth_token}", "Content-type": "application/json"}

    print(f'Sending MMS to number {number}: {payload}')
    response = requests.post(endpoint, json=payload, headers=headers)

    print(f'Simple SMS response: {response.json()}')

def send_plivo_text(number, mms_content, preview_image):
    if not phlo:
        phlo_client = plivo.phlo.RestClient(auth_id=phlo_auth_id, auth_token=phlo_auth_token)
        phlo = phlo_client.phlo.get(phlo_id)
    number = "+1" + number
    payload = {"to" : number,
           "imageUrl": preview_image,
           "message": mms_content}
    print(f'Sending MMS to number {number}: {payload}')
    response = phlo.run(**payload)
    print(f'Plivo response: {response}')

def send_twilio_text(number, mms_content, preview_image):
    if not tw_client:
        tw_client = Client(tw_account_sid, tw_auth_token)
    # TODO no preview_image for now. Changed to Twilio b/c Plivio sux
    number = "+1" + number
    print(f'Sending MMS to number {number}: {mms_content}')
    message = tw_client.messages.create(
        body=mms_content,
        # My number
        from_="+18447700833",
        to=number
    )
    print(f'Twilio message ID: {message.sid}')

def main():
    send_simple_sms_text("2102418565", "Testing testing", "https://jmattfong-halloween-public.s3.us-west-2.amazonaws.com/casey_256.jpg")

if __name__ == "__main__":
    main()
