"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# GET /users - Obtener todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_to_json = jsonify(user.serialize() for user in users), 200
    return users_to_json


# GET /users - Obtener por ID

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user is None:
       abort(404, description=f"Usuario con id {user_id} no encontrado")
    user_to_json = jsonify(user.serialize())
    return user_to_json, 200


# GET /planets - Obtener todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_to_json = jsonify([planet.serialize() for planet in planets]), 200
    return planets_to_json

# GET /planets - Obtener un planeta por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        abort(404, description=f"Planeta con id {planet_id} no encontrado")
    
    planet_to_json = jsonify(planet.serialize())
    return planet_to_json, 200

# POST /USER - crear usuario

@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()
    if body is None:
        abort(400, description="El bpdy no puee estar vacio")

    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in body or not body[field]:
            abort(422, description=f"el campo {field} es obligatorio")

    user_exists = User.query.filter_by(email=body['email']).first()
    if user_exists:
        abort(400, description="El email ya está registrado")

    try:
        new_user = User()
        new_user.email=body['email']
        new_user.password=body['password']
        new_user.first_name=body['first_name']  
        new_user.last_name=body['last_name']
        new_user.is_active = True

        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error real: {e}")
        abort(500, description="Error al crear usuario")

    
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user is None:
       abort(404, description=f"Usuario con id {user_id} no encontrado")

    try:
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": f"Usuario {user_id} eliminado con éxito"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        abort(500, description="Error al crear usuario")




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)