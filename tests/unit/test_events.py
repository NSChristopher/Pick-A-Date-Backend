import json

def test_create_event(client):
    
    payload = {
        "event_name": "Test Event",
        "description": "This is a test event",
        "max_date": "2025-12-31",
        "min_date": "2025-12-01",
        "lon": 0.0,
        "lat": 0.0,
    }

    response = client.post('/events/event', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 201
    
    response_json = response.get_json()

    assert response_json['status'] == 'success'

    assert response_json['data']['event_name'] == 'Test Event'
    assert response_json['data']['description'] == 'This is a test event'
    assert response_json['data']['max_date'] == '2025-12-31'
    assert response_json['data']['min_date'] == '2025-12-01'
    assert 'uuid' in response_json['data']

    return response_json['data']['uuid']

def test_get_event_by_uuid(client):
    
    payload = {
        "event_name": "Test Event",
        "description": "This is a test event",
        "max_date": "2025-12-31",
        "min_date": "2025-12-01",
        "lon": 0.0,
        "lat": 0.0,
    }

    response = client.post('/events/event', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 201
    
    response_json = response.get_json()

    assert response_json['status'] == 'success'

    assert response_json['data']['event_name'] == 'Test Event'
    assert response_json['data']['description'] == 'This is a test event'
    assert response_json['data']['max_date'] == '2025-12-31'
    assert response_json['data']['min_date'] == '2025-12-01'

    assert 'uuid' in response_json['data']

    uuid = response_json['data']['uuid']

    response = client.get(f'/events/event?uuid={uuid}')

    assert response.status_code == 200
    assert response.get_json()['data']['uuid'] == uuid
    assert response.get_json()['data']['event_name'] == 'Test Event'
    assert response.get_json()['data']['description'] == 'This is a test event'
    assert response.get_json()['data']['max_date'] == '2025-12-31'
    assert response.get_json()['data']['min_date'] == '2025-12-01'