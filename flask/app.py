from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import csv


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class UserAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<UserAction(user_id='{self.user_id}', action='{self.action}', timestamp='{self.timestamp}')>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    patronymic = db.Column(db.String(50))
    iin = db.Column(db.String(12))
    city = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    age = db.Column(db.Integer)

    def __repr__(self):
        return f"<User(surname='{self.surname}', name='{self.name}', patronymic='{self.patronymic}', iin='{self.iin}', city='{self.city}', nationality='{self.nationality}', age='{self.age}')>"

@app.route('/log_action', methods=['POST'])
def log_action():
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')
    timestamp = datetime.datetime.now()
    new_action = UserAction(user_id=user_id, action=action, timestamp=timestamp)
    db.session.add(new_action)
    db.session.commit()
    return jsonify({"message": "Action logged successfully"}), 200

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_actions')
def user_actions():
    user_actions = UserAction.query.all()
    return render_template('user_actions.html', user_actions=user_actions)


@app.route('/user_information')
def user_information():
    with open('userdata.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user_data = list(reader)
    return render_template('user_information.html', user_data=user_data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8088)

