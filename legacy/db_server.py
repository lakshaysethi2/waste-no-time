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


@app.route('/activity/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    try:
        activity = Activity.query.get(activity_id)
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Activity deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Activity not deleted', 'message': str(e)})


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




if __name__ == '__main__':
    app.run(debug=True)
