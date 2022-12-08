from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


with app.app_context():
    db.create_all()

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(120), nullable=True)
    def __repr__(self):
        return '<Activity %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    def __repr__(self):
        return '<User %r>' % self.name

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

@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user = User(name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    except Exception as e:
        return jsonify({'message': 'Error creating user', 'error': str(e)})
    finally:
        db.session.close()

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user = User.query.get(user_id)
        user.name = data['name']
        user.email = data['email']
        db.session.commit()
        return jsonify({'message': 'User updated successfully', 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    except Exception as e:
        return jsonify({'message': 'Error updating user', 'error': str(e)})
    finally:
        db.session.close()

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully', 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    except Exception as e:
        return jsonify({'message': 'Error deleting user', 'error': str(e)})
    finally:
        db.session.close()

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        return jsonify({'message': 'User retrieved successfully', 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    except Exception as e:
        return jsonify({'message': 'Error retrieving user', 'error': str(e)})
    finally:
        db.session.close()

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify({'message': 'Users retrieved successfully', 'users': [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]})
    except Exception as e:
        return jsonify({'message': 'Error retrieving users', 'error': str(e)})
    finally:
        db.session.close()

@app.route('/')
def home():
    return 'use the /activity api endpoint'


@app.route('/activity', methods=['POST'])
def create_activity():
    try:
        data = request.get_json()
        activity = Activity(name=data['name'], start_time=data['start_time'], end_time=data['end_time'], notes=data['notes'])
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'Activity created successfully', 'activity': {'id': activity.id, 'name': activity.name, 'start_time': activity.start_time, 'end_time': activity.end_time, 'notes': activity.notes}})
    except Exception as e:
        return jsonify({'error': 'Activity not created', 'message': str(e)})

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

@app.route('/activity/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    try:
        data = request.get_json()
        activity = Activity.query.get(activity_id)
        activity.name = data['name']
        activity.start_time = data['start_time']
        activity.end_time = data['end_time']
        activity.notes = data['notes']
        db.session.commit()
        return jsonify({'message': 'Activity updated successfully', 'activity': {'id': activity.id, 'name': activity.name, 'start_time': activity.start_time, 'end_time': activity.end_time, 'notes': activity.notes}})
    except Exception as e:
        return jsonify({'error': 'Activity not updated', 'message': str(e)})

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

@app.route('/activity/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    try:
        activity = Activity.query.get(activity_id)
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Activity deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Activity not deleted', 'message': str(e)})

def test_delete_activity():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        response1 = client.post('/activity', json=data)
        response = client.delete(f'/activity/{response1.json["activity"]["id"]}')
        assert response.status_code == 200
        assert response.json.keys() == {'message'}
        assert response.json['message'] == 'Activity deleted successfully'
        assert 'error' not in response.json.keys()

@app.route('/activity/<int:from_time>/<int:to_time>', methods=['GET'])
def get_activities(from_time, to_time):
    if from_time and to_time:
        activities = Activity.query.filter(Activity.start_time >= from_time, Activity.end_time <= to_time).all()
    else:
        return jsonify({'error': "Please provide from_time and to_time as query parameters"})
    output = []
    for activity in activities:
        activity_data = {'name': activity.name, 'start_time': activity.start_time, 'end_time': activity.end_time, 'notes': activity.notes}
        output.append(activity_data)
    return jsonify({'activities': output})

def test_get_activities():
    with app.test_client() as client:
        data = {'name': 'test', 'start_time': 123, 'end_time': 456, 'notes': 'test notes'}
        client.post('/activity', json=data)
        response = client.get('/activity/3/1000')
        assert response.status_code == 200
        assert response.json.keys() == {'activities'}
        assert len(response.json['activities']) > 0
        assert 'error' not in response.json.keys()



if __name__ == '__main__':
    app.run(debug=True)
