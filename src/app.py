"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from api.models import User

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

#  Configura la extensión Flask-JWT-Extended
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET') # ESTA PALABRA ES LO QUE GENERA LUEGO LOS TOKENS UNICOS Y LO QUE NO SE DEBE COMPARTIR # ¡Cambia las palabras "super-secret" por otra cosa!
jwt = JWTManager(app)                               # LA PONGO EN ENV PARA NO SUBIRLO A LA NUBE Y QUE SEA SECRETA

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

@app.route("/signup", methods=["POST"])
def signup():
    body = request.json

    if body["email"] == None or body["pass"] == None:
        return jsonify({"msg": "Insert and email or password"}), 400

    # Crear un nuevo usuario en la base de datos
    new_user = User(email = body["email"], password = body["pass"], is_active = True)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"code": 200, "mensaje": "Usuario creado correctamente"})

@app.route("/users", methods=["GET"])
def users():

    try:

        query = db.select(User).order_by(User.id)
        users = db.session.execute(query).scalars()

        user_list = [user.serialize() for user in users]

        return {"code": 200, "msg": "Usuarios existentes obtenidos", "users": user_list}

    except Exception as error:
        print(error)
        return jsonify(users_response), users_response["code"]

# Crea una ruta para autenticar a los usuarios y devolver el token JWT.
# La función create_access_token() se utiliza para generar el JWT.
@app.route("/token", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("pass", None)

    # Consulta la base de datos por el nombre de usuario y la contraseña
    # user = User.filter.query(email=email).first()                   # No se como hacer esta query segun el metodo de la academia
    query = db.session.query(User).filter(User.email == email)

    user = db.session.execute(query).scalars().one()

    if user is None:
        # el usuario no se encontró en la base de datos
        return jsonify({"msg": "Bad email or password"}), 401       # SIEMPRE PONER EMAIL O PASS, NUNCA DECIR 1 SOLA DE LAS 2 ESTÁ MAL, MUCHA INFORMACIÓN GRATIS PARA LOS HACKERS

    
    # HARCODEANDO PRUEBA FACIL DE EMAIL
    # if email != "test" or password != "test":
    #     return jsonify({"msg": "Bad email or password"}), 401

    if password == user.password:
        # crea un nuevo token con el id de usuario dentro
        access_token = create_access_token(identity=user.serialize())
        return jsonify({ "token": access_token, "user": user.serialize() })
    else:
        return jsonify({"msg": "Bad email or password"}), 401       # SIEMPRE PONER EMAIL O PASS, NUNCA DECIR 1 SOLA DE LAS 2 ESTÁ MAL, MUCHA INFORMACIÓN GRATIS PARA LOS HACKERS

# Protege una ruta con jwt_required, bloquea las peticiones
# sin un JWT válido presente.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Accede a la identidad del usuario actual con get_jwt_identity
    current_user = get_jwt_identity()
    # user = User.filter.get(current_user_email)            # No se como hacer esta query segun el metodo de la academia

    query = db.session.query(User).filter(User.email == current_user["email"])
    user = db.session.execute(query).scalars().one()

    access_token = create_access_token(identity=user.serialize())

    return jsonify({ "code": 200, "msg": "Inicio de sesión correcto", "token": access_token, "user": user.serialize() }), 200




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
