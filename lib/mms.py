#!/usr/bin/env python3

import plivo

auth_id = 'MAYWJHZDJKYZZLN2Y1OT'
auth_token = 'M2JlMWQ4N2I0YWVlN2VlMTg4ZGUwMjY1MmRiYjk4'
phlo_id = '54f33751-1f35-47a2-be06-e894360a22c0'

phlo_client = plivo.phlo.RestClient(auth_id=auth_id, auth_token=auth_token)
phlo = phlo_client.phlo.get(phlo_id)

def send_text(number, mms_content, preview_image):
    number = "+1" + number
    payload = {"to" : number, 
           "imageUrl": preview_image,
           "message": mms_content}
    print(f'Sending MMS to number {number}: {payload}')
    response = phlo.run(**payload)
    print(f'Plivo response: {response}')
