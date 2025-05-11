import json
from .test_events import test_create_event
from .test_participants import test_create_participant

# def test_create_date(client):
    
#     payload = {
#         "event_id": 1,
#         "user_id": 1,
#         "date": "2025-12-31",
#         "is_blocked": False,
#     }

#     response = client.post('/dates/date', data=json.dumps(payload), content_type='application/json')

#     assert response.status_code == 201

#     response_json = response.get_json()

#     assert response_json['status'] == 'success'
#     assert response_json['data']['event_id'] == 1
#     assert response_json['data']['user_id'] == 1
#     assert response_json['data']['date'] == '2025-12-31'
#     assert response_json['data']['is_blocked'] == False

#     return response_json['data']['date_id']

# def test_get_date_by_event_id(client):
    
#     event_uuid = test_create_event(client)
#     user_id = test_create_user(client)
#     date_id = test_create_date(client)

#     response = client.get(f'/dates/date?event_id=1')

#     assert response.status_code == 200

#     assert response.get_json()['status'] == 'success'

# def test_get_date_by_event_id_and_user_id(client):
    
#     event_uuid = test_create_event(client)
#     user_id = test_create_user(client)
#     date_id = test_create_date(client)

#     response = client.get(f'/dates/date?event_id=1&user_id=1')

#     assert response.status_code == 200

#     assert response.get_json()['status'] == 'success'

# def test_delete_date(client):
    
#     event_uuid = test_create_event(client)
#     user_id = test_create_user(client)
#     date_id = test_create_date(client)

#     payload = {
#         "date_id": date_id,
#         "user_id": user_id
#     }

#     response = client.delete('/dates/date', data=json.dumps(payload), content_type='application/json')

#     assert response.status_code == 200

#     assert response.get_json()['status'] == 'success'