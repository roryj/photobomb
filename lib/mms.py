#!/usr/bin/env python3

import plivo

auth_id = 'MAYWJHZDJKYZZLN2Y1OT'
auth_token = 'M2JlMWQ4N2I0YWVlN2VlMTg4ZGUwMjY1MmRiYjk4'
phlo_id = '54f33751-1f35-47a2-be06-e894360a22c0'

rory="+12068831424"
matt="+12102418565"

payload = {"to" : rory, 
           "imageUrl": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/35d305c8-432c-460f-a4ae-d9a00c1c9776/d74x8xb-dc74469b-8b70-42eb-88e0-95be98d9428f.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzM1ZDMwNWM4LTQzMmMtNDYwZi1hNGFlLWQ5YTAwYzFjOTc3NlwvZDc0eDh4Yi1kYzc0NDY5Yi04YjcwLTQyZWItODhlMC05NWJlOThkOTQyOGYucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.023NwOfMuH0qhLjjF_3_aO81kSvLqm6F-BiKkIxRk_c",
           "message": "say my name"}
phlo_client = plivo.phlo.RestClient(auth_id=auth_id, auth_token=auth_token)
phlo = phlo_client.phlo.get(phlo_id)
response = phlo.run(**payload)

print(response)
