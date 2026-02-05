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
from models import db, User, Planet, Character, Vehicle, Favorite
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
    users_to_json = jsonify([user.serialize() for user in users]), 200
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


# GET/ todos los vehículos
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    all_vehicles = Vehicles.query.all()
    vehicles_to_json = jsonify([vehicle.serialize() for vehicle in all_vehicles]), 200
    
    return vehicles_to_json


# GET  vehículo por ID
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id(vehicle_id):
    vehicle = Vehicles.query.get(vehicle_id)
    
    if vehicle is None:
        
        abort(404, description=f"Vehículo con id {vehicle_id} no encontrado")
    
    vehicle_to_json = jsonify(vehicle.serialize())
    return vehicle_to_json, 200

# GET / personajes
@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Character.query.all()
    characters_to_json = jsonify([character.serialize() for character in all_characters]), 200
    
    return characters_to_json


# GET personaje por ID
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    character = Character.query.get(character_id)
    
    if character is None:
        abort(404, description=f"Personaje con id {character_id} no encontrado")
    
    character_to_json = jsonify(character.serialize())
    return character_to_json, 200

# POST /USER - crear usuario

@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()
    if body is None:
        abort(400, description="El body no puede estar vacio")

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



        
# POST /planets - Crear un nuevo planeta

@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()
    
    if body is None:
        abort(400, description="El body no puede estar vacio")
    
    try:
        new_planet = Planet()
        
        new_planet.name = body['name']
        new_planet.climate = body['climate']
        new_planet.terrain = body['terrain']
        new_planet.population = body['population']
    
        db.session.add(new_planet)
        db.session.commit()

        return jsonify(new_planet.serialize()), 201

    except Exception as e:
        db.session.rollback()
        abort(500, description="Error al crear el planeta")


# POST /vehicles - Crear un nuevo vehiculo

@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    body = request.get_json()
    
    if body is None:
        abort(400, description="El body no puede estar vacio")
    
    try:
        new_vehicle = Vehicles()
        
        new_vehicle.name = body['name']
        new_vehicle.cargo_capacity = body['cargo_capacity']
        new_vehicle.length = body['length']
        new_vehicle.model = body['model']
    
        db.session.add(new_vehicle)
        db.session.commit()

        return jsonify(new_vehicle.serialize()), 201

    except Exception as e:
        db.session.rollback()
        abort(500, description="Error al crear el vehiculo")


# POST /character - Crear un nuevo character

@app.route('/characters', methods=['POST'])
def create_character():
    body = request.get_json()
    
    if body is None:
        abort(400, description="El body no puede estar vacio")
    
    try:
        new_character = Character()
        
        new_character.name = body['name']
        new_character.gender = body['gender']
        new_character.height = body['height']
        new_character.mass = body['mass']
    
        db.session.add(new_character)
        db.session.commit()

        return jsonify(new_character.serialize()), 201

    except Exception as e:
        db.session.rollback()
        abort(500, description="Error al crear el personaje")



# DELETE user

    
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
        abort(500, description="Error al eliminar usuario")


# DELETE planet

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
       abort(404, description=f"Planeta con id {planet_id} no encontrado")

    try:
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": f"Planeta {planet_id} eliminado con éxito"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        abort(500, description="Error al eliminar el planeta")


# DELETE vehicle

@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    # Recuerda: Usamos Vehicles (mayúscula y plural) por tu models.py
    vehicle = Vehicles.query.get(vehicle_id)

    if vehicle is None:
       abort(404, description=f"Vehículo con id {vehicle_id} no encontrado")

    try:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({"msg": f"Vehículo {vehicle_id} eliminado con éxito"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        abort(500, description="Error al eliminar el vehículo")



# DELETE character

@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)

    if character is None:
       abort(404, description=f"Personaje con id {character_id} no encontrado")

    try:
        db.session.delete(character)
        db.session.commit()
        return jsonify({"msg": f"Personaje {character_id} eliminado con éxito"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        abort(500, description="Error al eliminar el personaje")



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)