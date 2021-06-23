"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Profesional, Person, Appointment, Report, Exercise
from flask_jwt_extended import create_access_token, JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "01cdeef14f0a17d28d723f35a2ba3670"
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.json
    print(f"data: {data}")
    user = User.create(name=data.get('name'), last_name= data.get('last_name'), email=data.get('email'), password=data.get('password')
    )
    
    if not isinstance(user, User):
        return jsonify({'msg': "Ha ocurrido un problema"}), 500
    return jsonify(user.serialize()), 201

@app.route('/sign-up-profesional', methods=['POST'])
def sign_up_profesional():
    data = request.json
    print(f"data: {data}")
    profesional = Profesional.create_profesional(name=data.get('name'), last_name= data.get('last_name'), email=data.get('email'), password=data.get('password'), is_verified=data.get('is_verified')
    )
    
    if not isinstance(profesional, Profesional):
        return jsonify({'msg': "Ha ocurrido un problema"}), 500
    return jsonify(profesional.serialize()), 201

@app.route('/log-in', methods=["POST"])
def log_in():
    data = request.json
    print(f"data: {data}")
    user = User.query.filter_by(email=data['email']).one_or_none()

    if user is None:
        return jsonify({"msg": "El user no existe"}), 404

    if not user.check_password(data.get('password')):
        return jsonify({"msg": "bad credentials"}), 400

    token = create_access_token(identity=user.id)
    
    return jsonify({
        "user": user.serialize(),
        "token": token
        }), 200

@app.route("/profesionals", methods=["GET"])
def get_profesionals():
    profesionals = Profesional.query.all();
    profesionals_to_list = list(map(lambda el: el.serialize(), profesionals))
    return jsonify(profesionals_to_list), 200

@app.route("/profesionals/<int:id>", methods=["GET"])
def get_profesional(id):
    profesional = Profesional.query.filter_by(id=id)
    profesional_to_list = list(map(lambda el: el.serialize(), profesional))
    return jsonify(profesional_to_list), 200



@app.route('/<int:id>/dates', methods=['GET','POST'])
def dates(id):
    if request.method == 'POST':
        data = request.json
        new_dict = {
            "date": data["data"]["date"],
            "schedule": data["data"]["schedule"],
            "via": data["data"]["via"],
            "profesional_id": data["data"]["profesional_id"]
        }

        appointment = Appointment.create(day_date=new_dict.get('date'), schedule= new_dict.get('schedule'), via=new_dict.get('via'), user_id=id, profesional_id=new_dict.get('profesional_id'))
        
        print(appointment)
        if not isinstance(appointment, Appointment):
            return jsonify({'msg': "Ha ocurrido un problema"}), 500
        return jsonify(appointment.serialize()), 201
    else:
        appointment = Appointment.query.filter_by(user_id=id).all()
        appointment_to_list = list(map(lambda el: el.serialize(), appointment))
        return jsonify(appointment_to_list), 200


@app.route('/<int:id>/reports', methods=['GET','POST'])
def reports(id):
    if request.method == 'POST':
        data = request.json
        new_dict = {
            "diagnostic": data["data"]["diagnostic"],
            "exercise_id": data["data"]["exercise_id"],
            "user_id": data["data"]["user_id"]
        }

        report = Report.create(diagnostic=new_dict.get('diagnostic'), exercise_id= new_dict.get('exercise_id'), profesional_id=id, user_id=new_dict.get('user_id'))
        
        print(report)
        if not isinstance(report, Report):
            return jsonify({'msg': "Ha ocurrido un problema"}), 500
        return jsonify(report.serialize()), 201
    else:
        report = Report.query.filter_by(user_id=id).all()
        report_to_list = list(map(lambda el: el.serialize(), report))
        return jsonify(report_to_list), 200

@app.route('/<int:id>/reports', methods=['GET','POST'])
def exercises(id):
    if request.method == 'POST':
        data = request.json
        new_dict = {
            "description": data["data"]["description"],
            "status": data["data"]["status"],
        }

        exercise = Exercise.create(description=new_dict.get('description'), status= new_dict.get('status'), exercise_id=id)
        
        print(exercise)
        if not isinstance(exercise, Exercise):
            return jsonify({'msg': "Ha ocurrido un problema"}), 500
        return jsonify(exercise.serialize()), 201
    else:
        exercise = Exercise.query.filter_by(exercise_id=id).all()
        exercise_to_list = list(map(lambda el: el.serialize(), exercise))
        return jsonify(exercise_to_list), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
