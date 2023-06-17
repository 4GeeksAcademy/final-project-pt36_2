"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, User, Muestra
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "last_name": user.last_name,
            "rut": user.rut,
            "email": user.email,
            "rol": user.rol
        })
    return jsonify(result)

@app.route('/user/<string:email>', methods=['GET'])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify(user.serialize())

@app.route('/user/rol/<string:rol>', methods=['GET'])
def get_users_by_role(rol):
    users = User.query.filter_by(rol=rol).all()
    if len(users) == 0:
        return jsonify({'message': 'No se encontraron usuarios con ese rol'}), 404

    serialized_users = [user.serialize() for user in users]
    return jsonify(serialized_users)




@app.route('/user', methods=['POST'])
def create_user():
    data = request.json

    user = User(
        name=data['name'],
        last_name=data['last_name'],
        rut=data['rut'],
        email=data['email'],
        rol=data['rol'],
        password=data['password']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuario creado correctamente'})


@app.route('/muestra', methods=['POST'])
def create_muestra():
    data = request.json

    muestra = Muestra(
        project_name=data['project_name'],
        ubication=data['ubication'],
        ubication_image=data['ubication_image'],
        area=data['area'],
        specimen=data['specimen'],
        quality_specimen=data['quality_specimen'],
        image_specimen=data['image_specimen'],
        aditional_comments=data['aditional_comments']
    )

    db.session.add(muestra)
    db.session.commit()

    return jsonify({'message': 'Muestra  creada correctamente'})


@app.route('/muestra', methods=['GET'])
def get_muestra():
    muestras = Muestra.query.all()
    result = list(map(lambda muestr:muestr.serialize(),muestras))
    return jsonify(result)

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Buscar el usuario por su ID
    user = User.query.get(user_id)

    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Eliminar el usuario de la base de datos
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Usuario eliminado correctamente'})


@app.route('/muestra/<int:muestra_id>', methods=['DELETE'])
def delete_muestra(muestra_id):
    # Buscar la muestra por su ID
    muestra = Muestra.query.get(muestra_id)

    if muestra is None:
        return jsonify({'message': 'Muestra no encontrada'}), 404

    # Eliminar la muestra de la base de datos
    db.session.delete(muestra)
    db.session.commit()

    return jsonify({'message': 'Muestra eliminada correctamente'})



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
