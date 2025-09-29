
from flask import Flask, request, jsonify, g, make_response
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import base64

DATABASE = 'tareas.db'
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    ''')
    db.commit()

def parse_basic_auth(auth_header: str):
    if not auth_header:
        return None, None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'basic':
        return None, None
    try:
        decoded = base64.b64decode(parts[1]).decode('utf-8')
        username, password = decoded.split(':', 1)
        return username, password
    except Exception:
        return None, None

def verify_credentials(username: str, password: str) -> bool:
    db = get_db()
    cur = db.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    row = cur.fetchone()
    if not row:
        return False
    return check_password_hash(row['password_hash'], password)

# endpoints
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'JSON requerido'}), 400
    username = data.get('usuario')
    password = data.get('contraseña')
    if not username or not password:
        return jsonify({'error': 'usuario y contraseña requeridos'}), 400
    password_hash = generate_password_hash(password)
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'usuario ya existe'}), 409

    return jsonify({'message': 'usuario registrado exitosamente'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'JSON requerido'}), 400
    username = data.get('usuario')
    password = data.get('contraseña')
    if not username or not password:
        return jsonify({'error': 'usuario y contraseña requeridos'}), 400
    if verify_credentials(username, password):
        return jsonify({'message': 'login exitoso'}), 200
    else:
        return jsonify({'error': 'credenciales inválidas'}), 401

@app.route('/tareas', methods=['GET'])
def tareas():
    auth_header = request.headers.get('Authorization')
    username, password = parse_basic_auth(auth_header)
    if not username or not password:
        resp = make_response('<h1>Acceso no autorizado</h1>', 401)
        resp.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
        return resp
    if not verify_credentials(username, password):
        resp = make_response('<h1>Credenciales inválidas</h1>', 401)
        resp.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
        return resp
    
if __name__ == '__main__':
    with app.app_context():
        init_db()
    print('Iniciando servidor en http://127.0.0.1:5000')
    app.run(debug=True)