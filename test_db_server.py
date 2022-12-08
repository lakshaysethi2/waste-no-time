from db_server import app, db
with app.app_context():
    db.create_all()


def test_create_user():
    with app.test_client() as client:
        data = {'name': 'test', 'email': 'test@test.com'}
        response = client.post('/user', json=data)
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'user'}
        assert response.json['message'] == 'User created successfully'
        assert response.json['user'].keys() == {'id', 'name', 'email'}
        assert 'error' not in response.json['user'].keys()
        assert response.json['user']['name'] == 'test'
        assert response.json['user']['email'] == 'test@test.com'

def test_update_user():
    with app.test_client() as client:
        data = {'name': 'test', 'email': 'test@test.com'}
        response1 = client.post('/user', json=data)
        data = {'name': 'test', 'email': 'test2@test.com'}
        response = client.put(f'/user/{response1.json["user"]["id"]}', json=data)
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'user'}
        assert response.json['message'] == 'User updated successfully'
        assert response.json['user'].keys() == {'id', 'name', 'email'}
        assert 'error' not in response.json['user'].keys()
        assert response.json['user']['name'] == 'test'
        assert response.json['user']['email'] == 'test2@test.com'

def test_delete_user():
    with app.test_client() as client:
        data = {'name': 'test', 'email': 'test@test.com'}
        response1 = client.post('/user', json=data)
        response = client.delete(f'/user/{response1.json["user"]["id"]}')
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'user'}
        assert response.json['message'] == 'User deleted successfully'
        assert response.json['user'].keys() == {'id', 'name', 'email'}
        assert 'error' not in response.json['user'].keys()
        assert response.json['user']['name'] == 'test'
        assert response.json['user']['email'] == 'test@test.com'

def test_get_user():
    with app.test_client() as client:
        data = {'name': 'test', 'email': 'test@test.com'}
        response1 = client.post('/user', json=data)
        response = client.get(f'/user/{response1.json["user"]["id"]}')
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'user'}
        assert response.json['message'] == 'User retrieved successfully'
        assert response.json['user'].keys() == {'id', 'name', 'email'}
        assert 'error' not in response.json['user'].keys()
        assert response.json['user']['name'] == 'test'
        assert response.json['user']['email'] == 'test@test.com'

def test_get_all_users():
    with app.test_client() as client:
        data = {'name': 'test', 'email': 'test@test.com'}
        response1 = client.post('/user', json=data)
        response = client.get('/users')
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'users'}
        assert response.json['message'] == 'Users retrieved successfully'
        assert response.json['users'][0].keys() == {'id', 'name', 'email'}
        assert 'error' not in response.json['users'][0].keys()



def test_create_activity():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        response = client.post('/activity', json=data)
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'activity'}
        assert response.json['message'] == 'Activity created successfully'
        assert response.json['activity'].keys() == {'id', 'name', 'start_time', 'end_time', 'notes'}
        assert 'error' not in response.json['activity'].keys()
        assert response.json['activity']['name'] == 'test'
        assert response.json['activity']['start_time'] == 123
        assert response.json['activity']['end_time'] == 456
        assert response.json['activity']['notes'] == 'test notes'


def test_update_activity():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        response1 = client.post('/activity', json=data)
        data = {'name': 'test', 'start_time': 123, 'end_time': 458, 'notes': 'test notes'}
        response = client.put(f'/activity/{response1.json["activity"]["id"]}', json=data)
        assert response.status_code == 200
        assert response.json.keys() == {'message', 'activity'}
        assert response.json['message'] == 'Activity updated successfully'
        assert response.json['activity']['end_time'] == 458
        assert 'error' not in response.json.keys()

def test_delete_activity():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        response1 = client.post('/activity', json=data)
        response = client.delete(f'/activity/{response1.json["activity"]["id"]}')
        assert response.status_code == 200
        assert response.json.keys() == {'message'}
        assert response.json['message'] == 'Activity deleted successfully'
        assert 'error' not in response.json.keys()

def test_get_activities():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        client.post('/activity', json=data)
        response = client.get('/activity/3/1000')
        assert response.status_code == 200
        assert response.json.keys() == {'activities'}
        assert len(response.json['activities']) > 0
        assert 'error' not in response.json.keys()