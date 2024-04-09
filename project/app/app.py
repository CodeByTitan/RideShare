#!/usr/bin/env python3
import cgi
import cgitb
import sys
import pymysql.cursors
import pymysql
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import ssl #include ssl libraries

import settings # Our server and db settings, stored in settings.py

app = Flask(__name__)
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)



####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

@app.errorhandler(500) # decorators to add to 500 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Internal server error' } ), 500)

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Casper", "password": "crap"}'
	#  	-c cookie-jar -k https://cs3103.cs.unb.ca:61340/signin
	#
	def post(self):

		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request

		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				response = {'status': 'success' }
				responseCode = 201
			except LDAPException:
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	# GET: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar
	#	-k https://cs3103.cs.unb.ca:61340/signin
	def get(self):
		success = False
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

	# DELETE: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar
	# 	-k https://info3103.cs.unb.ca:61340/signin

	#
	#	Here's your chance to shine!
	#
	def delete(self):
		session.pop('username', None)
		response = {'status': 'success'}
		responseCode = 204
		return make_response(jsonify(response), responseCode)


####################################################################################
#
# Identify/create endpoints and endpoint objects
#
class User(Resource):
	@app.route('/adduser', methods=['POST'])
def add_user():
    data = request.get_json()
    try:
        result = query_db(None, (data['userName'], data['Email'], data['PhoneNumber']), proc='adduser')
        if result:
            return jsonify({'UserId': result[0]['LAST_INSERT_ID()']}), 201
    except Exception as e:
        app.logger.error(f'Error adding user: {str(e)}')
        abort(500)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    email = request.form.get('email')  # Assuming you have an email field in your form
    phoneNumber = request.form.get('phoneNumber')  # Assuming you have a phoneNumber field in your form

    if not all([username, password, password_confirm, email, phoneNumber]):
        return jsonify({'status': 'fail', 'message': 'All fields are required'}), 400

    if password != password_confirm:
        return jsonify({'status': 'fail', 'message': 'Passwords do not match'}), 400

    # Hash the password for storage
    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('adduser', [username, email, phoneNumber])
            result = cursor.fetchone()  # Fetch the result of the SELECT LAST_INSERT_ID()
            conn.commit()

            # Check if we got a result back
            if result:
                userId = result['LAST_INSERT_ID()']
                # You might want to store the hashed password in a separate operation if your procedure doesn't handle it
                # cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, userId))
                # conn.commit()

                session['username'] = username  # Log the user in
                return redirect(url_for('home')), 302
            else:
                return jsonify({'status': 'fail', 'message': 'Signup failed'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn:
            conn.close()


	@app.route('/')
def home():
    # Check if user is logged in
    if 'username' in session:
        # Serve a different template or data if user is authenticated
        return render_template('dashboard.html', username=session['username'])
    return render_template('index.html')

	def post(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# The request object holds the ... wait for it ... client request!
		# Pull the results out of the json request
		username2 = request.json['Username'];
		email = request.json['Email'];
		phoneNumber = request.json['PhoneNumber'];

		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'adduser'
			cursor = dbConnection.cursor()
			sqlArgs = (username2, email, phoneNumber) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = str(row['LAST_INSERT_ID()'])
		return make_response(jsonify( { "UserId" : uri } ), 201) # successful resource creation

	def put(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# The request object holds the ... wait for it ... client request!
		# Pull the results out of the json request
		userId = request.json['UserId'];
		username2 = request.json['Username'];
		email = request.json['Email'];
		phoneNumber = request.json['PhoneNumber'];

		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'updateuser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,username2, email, phoneNumber) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		response = {'status': 'success'}
		responseCode = 200
		return make_response(jsonify(response), responseCode)
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		userId = request.json['UserId'];
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'getuser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"user": row}), 200) # successful
	def delete(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		userId = request.json['UserId'];
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'deluser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		response = {'status': 'success'}
		responseCode = 204
		return make_response(jsonify(response), responseCode)
class Ride(Resource):
	def put(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# The request object holds the ... wait for it ... client request!
		# Pull the results out of the json request
		driverId = request.json['DriverId'];
		rideId = request.json['RideId'];

		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'addDriver'
			cursor = dbConnection.cursor()
			sqlArgs = (driverId,rideId) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		response = {'status': 'success'}
		responseCode = 200
		return make_response(jsonify(response), responseCode)
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		rideId = request.json['RideId'];
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'getride'
			cursor = dbConnection.cursor()
			sqlArgs = (rideId,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"ride": row}), 200) # successful
	def post(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# The request object holds the ... wait for it ... client request!
		# Pull the results out of the json request
		startAddress = request.json['StartAddress'];
		endAddress = request.json['EndAddress'];
		cost = request.json['Cost'];
		riderId = request.json['RiderId'];
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'addride'
			cursor = dbConnection.cursor()
			sqlArgs = (startAddress, endAddress, cost, riderId) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		# Look closely, Grasshopper: we just created a new resource, so we're
		# returning the uri to it, based on the return value from the stored procedure.
		# Yes, now would be a good time check out the procedure.
		uri = str(row['LAST_INSERT_ID()'])
		return make_response(jsonify( { "RideId" : uri } ), 201) # successful resource creation
	def delete(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		riderId = request.json['RiderId'];
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'delride'
			cursor = dbConnection.cursor()
			sqlArgs = (riderId,) # Must be a collection
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			dbConnection.commit() # database was modified, commit the changes
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		response = {'status': 'success'}
		responseCode = 204
		return make_response(jsonify(response), responseCode)

@app.route('/rides')
def available_rides():
    rides = [
        {'id': 1, 'start': 'City Center', 'end': 'University', 'driver': 'John Doe', 'date': '2024-04-01', 'cost': '$10'},
        {'id': 2, 'start': 'Airport', 'end': 'Downtown', 'driver': 'Jane Smith', 'date': '2024-04-02', 'cost': '$15'}
    ]
    return render_template('available_rides.html', rides=rides)

def rides():
    # Logic to fetch rides and render template
    return render_template('rides.html')

class Rides(Resource):
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(host=settings.MYSQL_HOST,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               database=settings.MYSQL_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
			sql = 'getAvailableRides'
			cursor = dbConnection.cursor()
			cursor.callproc(sql) # stored procedure, with arguments
			rows = cursor.fetchall()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"rides": rows}), 200) # successful
api = Api(app)
api.add_resource(SignIn, '/signin')
api.add_resource(User, '/user')
api.add_resource(Ride, '/ride')
api.add_resource(Rides, '/rides')
	

#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	#
	# You need to generate your own certificates. To do this:
	#	1. cd to the directory of this app
	#	2. run the makeCert.sh script and answer the questions.
	#	   It will by default generate the files with the same names specified below.
	#
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
