import json

from .test_events import create_event

participan_payload = {
  "name": "John Doe",
  "phone": "1234567890",
  "postal_code": "12345",
  "is_driver": False
}

def create_participant(client, payload=None, token=None):
    if payload is None:
        payload = participan_payload

    if token is None:
        token = create_event(client).get_json()['data']['token']

    response = client.post(f'/events/{token}/participants', data=json.dumps(payload), content_type='application/json')
    return response

def test_create_participant(client):
    response = create_participant(client)

    assert response.status_code == 201

    response_json = response.get_json()

    assert response_json['status'] == 'success'
    assert response_json['data']['name'] == participan_payload['name']
    assert response_json['data']['phone'] == participan_payload['phone']
    assert response_json['data']['postal_code'] == participan_payload['postal_code']
    assert response_json['data']['is_driver'] == participan_payload['is_driver']
    assert 'participant_id' in response_json['data']
    
    return response_json['data']['participant_id']


def get_participant_by_phone(client, phone=None):
    if phone is None:
        phone = participan_payload['phone']

    token = create_event(client).get_json()['data']['token']

    create_participant(client, token=token)

    response = client.get(f'/events/{token}/participants/{phone}')
    return response

def test_get_participant_by_phone(client):
    response = get_participant_by_phone(client)

    assert response.status_code == 200

    response_json = response.get_json()

    assert response_json['status'] == 'success'
    assert response_json['data']['name'] == participan_payload['name']
    assert response_json['data']['phone'] == participan_payload['phone']
    assert response_json['data']['postal_code'] == participan_payload['postal_code']
    assert response_json['data']['is_driver'] == participan_payload['is_driver']
    assert 'participant_id' in response_json['data']

def get_participant_by_token(client, token=None):
    if token is None:
        token = create_event(client).get_json()['data']['token']

    create_participant(client, token=token)

    response = client.get(f'/events/{token}/participants')
    return response

def test_get_participant_by_token(client):
    response = get_participant_by_token(client)
    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json['status'] == 'success'
    assert len(response_json['data']['participants']) > 0
    assert 'participant_id' in response_json['data']['participants'][0]
    assert response_json['data']['participants'][0]['name'] == participan_payload['name']