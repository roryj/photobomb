#!/usr/bin/env python3

import plivo

auth_id = 'MAYWJHZDJKYZZLN2Y1OT'
auth_token = 'M2JlMWQ4N2I0YWVlN2VlMTg4ZGUwMjY1MmRiYjk4'
phlo_id = '54f33751-1f35-47a2-be06-e894360a22c0'

phlo_client = plivo.phlo.RestClient(auth_id=auth_id, auth_token=auth_token)
phlo = phlo_client.phlo.get(phlo_id)

def send_text(number, unspooked_url, spooked_url, preview_image='https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/72/d9/21/72d92136-dd8b-42c0-8d87-c242fa6468c7/source/256x256bb.jpg'):
    number = "+1" + number
    payload = {"to" : number, 
           "imageUrl": preview_image,
           "message": f"Your Halloween Photobooth photos are ready! Download with the following links.\n\nSpooked: {spooked_url}\n\nOriginal: {unspooked_url}"}
    print(f'Sending MMS to number {number}')
    response = phlo.run(**payload)
    print(f'Plivo response: {response}')
