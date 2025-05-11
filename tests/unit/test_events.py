import json

event_payload = {
    "event_name": "test event",
    "description": "This is a test event",
    "max_date": "2025-05-31",
    "min_date": "2025-05-01",
    "addresses": [
        {
        "address_name": "Test Address",
        "street_line_1": "21 Test St",
        "street_line_2": "Apt 1",
        "city": "Test City",
        "state_or_province": "Test State",
        "country_code": "US",
        "postal_code": "12345",
        "latitude": 0.0,
        "longitude": 0.0
        }
    ]
}

# Create and test events

def create_event(client, payload=None):

    if payload is None:
        payload = event_payload

    response = client.post('/events', data=json.dumps(payload), content_type='application/json')
    return response

def test_create_event(client):
    response = create_event(client)

    assert response.status_code == 201
    data = response.get_json()

    assert data['status'] == 'success'
    assert 'token' in data['data']


# Get event by token

def get_event_by_token(client, token=None):

    if token is None:
        token = create_event(client).get_json()['data']['token']

    response = client.get(f'/events/{token}')
    return response

def test_get_event_by_token(client):

    response = get_event_by_token(client)

    assert response.status_code == 200

    response_json = response.get_json()

    assert response_json['status'] == 'success'
    assert response_json['data']['event_name'] == event_payload['event_name']
    assert response_json['data']['description'] == event_payload['description']