import json

def test_create_user(client):
    
    payload = {
        "event_id": 1,
        "name": "Test User",
        "phone": "1234567890",
        "lat": 0.0,
        "lon": 0.0,
        "is_driver": False
    }

    response = client.post('/users/user', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 201
    
    response_json = response.get_json()

    assert response_json['status'] == 'success'

    assert response_json['data']['event_id'] == 1
    assert response_json['data']['name'] == 'Test User'
    assert response_json['data']['phone'] == '1234567890'
    assert response_json['data']['lat'] == 0.0
    assert response_json['data']['lon'] == 0.0
    assert response_json['data']['is_driver'] == False

    assert 'user_id' in response_json['data']

    return response_json['data']['user_id']


def test_get_user_by_phone_and_event_id(client):
    
    payload = {
        "event_id": 1,
        "name": "Test User",
        "phone": "1234567890",
        "lat": 0.0,
        "lon": 0.0,
        "is_driver": False
    }

    response = client.post('/users/user', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 201
    
    response_json = response.get_json()

    assert response_json['status'] == 'success'

    assert response_json['data']['event_id'] == 1
    assert response_json['data']['name'] == 'Test User'
    assert response_json['data']['phone'] == '1234567890'
    assert response_json['data']['lat'] == 0.0
    assert response_json['data']['lon'] == 0.0
    assert response_json['data']['is_driver'] == False

    assert 'user_id' in response_json['data']

    user_id = response_json['data']['user_id']

    response = client.get(f'/users/user?phone=1234567890&event_id=1')

    assert response.status_code == 200
    assert response.get_json()['data']['user_id'] == user_id
    assert response.get_json()['data']['event_id'] == 1
    assert response.get_json()['data']['name'] == 'Test User'
    assert response.get_json()['data']['phone'] == '1234567890'
    assert response.get_json()['data']['lat'] == 0.0
    assert response.get_json()['data']['lon'] == 0.0
    assert response.get_json()['data']['is_driver'] == False