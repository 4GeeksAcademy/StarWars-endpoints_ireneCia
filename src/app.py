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
from models import db, User
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


# GET /users - Obtener todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


# GET /users/<id> - Obtener un usuario por ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"Usuario con id {user_id} no encontrado")
    return jsonify(user.serialize_with_profile()), 200


# POST /users - Crear un nuevo usuario
@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()

    if not body:
        abort(400, description="El body no puede estar vacío")

    # Validar campos obligatorios
    required_fields = ["email", "username", "password"]
    for field in required_fields:
        if field not in body or not body[field]:
            abort(400, description=f"El campo '{field}' es obligatorio")

    # Verificar que no exista un usuario con ese email o username
    existing_email = User.query.filter_by(email=body["email"]).first()
    if existing_email:
        abort(409, description="Ya existe un usuario con ese email")

    existing_username = User.query.filter_by(username=body["username"]).first()
    if existing_username:
        abort(409, description="Ya existe un usuario con ese username")

    try:
        new_user = User(
            email=body["email"],
            username=body["username"],
            password=body["password"],
            is_active=body.get("is_active", True)
        )
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Error al crear usuario")

    return jsonify(new_user.serialize()), 201


# PUT /users/<id> - Editar un usuario
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"Usuario con id {user_id} no encontrado")

    body = request.get_json()
    if not body:
        abort(400, description="El body no puede estar vacío")

    # Verificar duplicados si se intenta cambiar email o username
    if "email" in body and body["email"] != user.email:
        existing = User.query.filter_by(email=body["email"]).first()
        if existing:
            abort(409, description="Ya existe un usuario con ese email")
        user.email = body["email"]

    if "username" in body and body["username"] != user.username:
        existing = User.query.filter_by(username=body["username"]).first()
        if existing:
            abort(409, description="Ya existe un usuario con ese username")
        user.username = body["username"]

    if "password" in body:
        user.password = body["password"]
    if "is_active" in body:
        user.is_active = body["is_active"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Error al actualizar usuario")

    return jsonify(user.serialize()), 200


# DELETE /users/<id> - Eliminar un usuario
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"Usuario con id {user_id} no encontrado")

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Error al eliminar usuario")

    return jsonify({"message": f"Usuario '{user.username}' eliminado correctamente"}), 200


# POST /users/with-profile - Crear usuario con su perfil
@app.route('/users/with-profile', methods=['POST'])
def create_user_with_profile():
    body = request.get_json()

    if not body:
        abort(400, description="El body no puede estar vacío")

    # Validar campos obligatorios del usuario
    required_fields = ["email", "username", "password"]
    for field in required_fields:
        if field not in body or not body[field]:
            abort(400, description=f"El campo '{field}' es obligatorio")

    # Verificar duplicados
    if User.query.filter_by(email=body["email"]).first():
        abort(409, description="Ya existe un usuario con ese email")
    if User.query.filter_by(username=body["username"]).first():
        abort(409, description="Ya existe un usuario con ese username")

    try:
        new_user = User(
            email=body["email"],
            username=body["username"],
            password=body["password"],
            is_active=body.get("is_active", True)
        )

        # Crear el perfil asociado
        profile_data = body.get("profile", {})
        new_profile = ProfileInfo(
            first_name=profile_data.get("first_name"),
            last_name=profile_data.get("last_name"),
            phone=profile_data.get("phone"),
            address=profile_data.get("address"),
            bio=profile_data.get("bio"),
            avatar_url=profile_data.get("avatar_url")
        )
        new_user.profile = new_profile

        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Error al crear usuario con perfil")

    return jsonify(new_user.serialize_with_profile()), 201


# GET /users/<id>/orders - Obtener un usuario con sus órdenes
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"Usuario con id {user_id} no encontrado")
    return jsonify(user.serialize_with_orders()), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
