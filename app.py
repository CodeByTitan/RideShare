#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, session, render_template, redirect, url_for
from flask_restful import reqparse, Resource, Api
from flask_session import Session
from flask_cors import CORS

from werkzeug.security import generate_password_hash
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException
import pymysql.cursors
import pymysql
import settings  # Make sure you have a settings.py with necessary configurations


app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

api = Api(app)
CORS(app)
class SignIn(Resource):
    def post(self):
        print("==============================================================zxczxc=================================zczxczxczxc")
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args() 
        print(args)

        if args['username'] in session:
            return jsonify({'status': 'success'}), 200

        try:
            ldapServer = Server(host=settings.LDAP_HOST, use_ssl=True, get_info=ALL)
            with Connection(ldapServer, user=f'uid={args["username"]}, ou=People,ou=fcs,o=unb', password=args['password']) as ldapConnection:
                ldapConnection.bind()
                session['username'] = args['username']
                return {'status': 'success'}, 201
        except LDAPException as e:
                return {'status': 'Access denied', 'message': str(e)}, 403

    def get(self):
        if 'username' in session:
            return {'status': 'success'}, 200
        else:
            return {'status': 'Not signed in'}, 403

    def delete(self):
        session.pop('username', None)
        return jsonify({'status': 'success'}), 204

# Placeholder for User resource
class User(Resource):
    pass  # Implement methods as needed

# Placeholder for Ride resource
class Ride(Resource):
    pass  # Implement methods as needed

# Placeholder for listing all rides
class Rides(Resource):
    def get(self):
        pass  # Implement logic to fetch and return all rides

api.add_resource(SignIn, '/signin')
api.add_resource(User, '/user')
api.add_resource(Ride, '/ride')
api.add_resource(Rides, '/rides')

@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return render_template('index.html')

@app.route('/rides')
def available_rides():
    rides = [
        {'id': 1, 'start': 'City Center', 'end': 'University', 'driver': 'John Doe', 'date': '2024-04-01', 'cost': '$10'},
        {'id': 2, 'start': 'Airport', 'end': 'Downtown', 'driver': 'Jane Smith', 'date': '2024-04-02', 'cost': '$15'}
    ]
    return render_template('available_rides.html', rides=rides)

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')  # Path to your SSL certificates
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)
#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, session, render_template, redirect, url_for
from flask_restful import reqparse, Resource, Api
from flask_session import Session
from werkzeug.security import generate_password_hash
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException
import pymysql.cursors
import pymysql
import settings  # Make sure you have a settings.py with necessary configurations

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

api = Api(app)

class SignIn(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        if args['username'] in session:
            return jsonify({'status': 'success'}), 200

        try:
            ldapServer = Server(host=settings.LDAP_HOST, use_ssl=True, get_info=ALL)
            with Connection(ldapServer, user=f'uid={args["username"]}, ou=People,ou=fcs,o=unb', password=args['password']) as ldapConnection:
                ldapConnection.bind()
                session['username'] = args['username']
                return jsonify({'status': 'success'}), 201
        except LDAPException:
            return jsonify({'status': 'Access denied'}), 403

    def get(self):
        if 'username' in session:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'fail'}), 403

    def delete(self):
        session.pop('username', None)
        return jsonify({'status': 'success'}), 204

# Placeholder for User resource
class User(Resource):
    pass  # Implement methods as needed

# Placeholder for Ride resource
class Ride(Resource):
    pass  # Implement methods as needed

# Placeholder for listing all rides
class Rides(Resource):
    def get(self):
        pass  # Implement logic to fetch and return all rides

api.add_resource(SignIn, '/signin')
api.add_resource(User, '/user')
api.add_resource(Ride, '/ride')
api.add_resource(Rides, '/rides')

@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return render_template('index.html')

@app.route('/rides')
def available_rides():
    rides = [
        {'id': 1, 'start': 'City Center', 'end': 'University', 'driver': 'John Doe', 'date': '2024-04-01', 'cost': '$10'},
        {'id': 2, 'start': 'Airport', 'end': 'Downtown', 'driver': 'Jane Smith', 'date': '2024-04-02', 'cost': '$15'}
    ]
    return render_template('available_rides.html', rides=rides)

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')  # Path to your SSL certificates
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)
