from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import RPi.GPIO as GPIO    #Importamos la libreria RPi.GPIO
import time
import random#Importamos time para poder usar time.sleep
from flask import jsonify
from functools import wraps
from flask import request
from flask_cors import CORS
from time import sleep

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://jade:jade@localhost/solar_panels"
db = SQLAlchemy(app)
from models import SolarPanel

#Auxiliary function to authorize use
def validate_token(access_token):
    '''Verifies that an access-token is valid and
    meant for this app.

    Returns None on fail, and an e-mail on success'''
    '''h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
                           headers={'Host': 'www.googleapis.com',
                                    'Authorization': access_token})

    if not resp['status'] == '200':
        print(resp)
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    print(data['email'])
    return data['email']'''
    x = SolarPanel.query.filter_by(email=access_token).first()
    return x.id if x else None
    
#Decorator that will provide authorization
def authorized(fn):
    @wraps(fn)
    def check_auth(*args, **kwargs):
        if 'Authorization' not in request.headers:
            # Unauthorized
            print("No token in header")
            return 'Unauthorized', 404

        print("Checking token...")
        userid = validate_token(request.headers['Authorization'])
        if userid is None:
            print("Check returned FAIL!")
            # Unauthorized
            return 'Unauthorized', 404

        return fn(userid=userid, *args, **kwargs)
    return check_auth

#Auxiliary function to read the voltage amount the solar panel is generating
def read_voltage():
    #Retrieve voltage somehow
    voltage = 2
    return voltage
@app.route('/add')
def add():
    print('adding')
    e = SolarPanel(ip_address='0.0.0.0', name='Diego Betanzos', email='diegobtzeqr@gmail.com')
    db.session.add(e)
    db.session.commit()
    
#Endpoint that will provide the voltage generated by the panel at given moment
@app.route('/voltage')
@authorized
def voltage(userid):
    voltage = read_voltage()
    return jsonify({'voltage':voltage})

#Endpoint to rotate the solar panel in the y axis     
@app.route('/move_y/<float:y>', methods=['GET'])
@authorized
def move_solar_panel_y(userid,y):
    print('Moving the solar panel in y:', y)
    GPIO.setmode(GPIO.BOARD)   #Ponemos la Raspberry en modo BOARD
    GPIO.setup(16,GPIO.OUT)    #Ponemos el pin 12 como salida
    p = GPIO.PWM(16,50)
    p.start(7.5)  #Ponemos el pin 12 en modo PWM y enviamos 50 pulsos por segundo
    p.ChangeDutyCycle(y)
    sleep(0.5)#Enviamos un pulso del 4.5% para girar el servo hacia la izquierda
    return str(y)

#Endpoint to rotate the solar panel in the x axis
@app.route('/move_x/<float:x>')
@authorized
def move_solar_panel_x(userid,x):
    print('Moving the solar panel in x:', x)
    GPIO.setmode(GPIO.BOARD)   #Ponemos la Raspberry en modo BOARD
    #CAMBIAR EL PIN AL DEL OTRO MOTOR
    GPIO.setup(12,GPIO.OUT)    #Ponemos el pin 21 como salida
    p = GPIO.PWM(12,50)        #Ponemos el pin 21 en modo PWM y enviamos 50 pulsos por segundo
    p.start(7.5)
    p.ChangeDutyCycle(x)    #Enviamos un pulso del 4.5% para girar el servo hacia la izquierda
    sleep(0.5)
    return str(x)

#Endpoint that will search for the best position of the panel to be
@app.route('/search')
@authorized
def search_max_power(userid):
    print('Looking for the best position..')
    max_voltage = 0
    x_max = 0
    y_max = 0
    x_start = 2.55
    y_start = 6.2
    x_final = 11.45
    y_final = 10.0
    step = 1
    
    GPIO.setmode(GPIO.BOARD)   
    
    #Prepare pins
    GPIO.setup(16,GPIO.OUT)
    y = GPIO.PWM(16,50)
    
    GPIO.setup(12,GPIO.OUT)    
    x = GPIO.PWM(12,50)        #Ponemos el pin 21 en modo PWM y enviamos 50 pulsos por segundo
    
    #Set panel on starting position
    x.start(x_start)
    sleep(0.5)
    y.start(y_start)
    sleep(0.5)
    
    while x_start < x_final:
        y_start = 6.2
        y.ChangeDutyCycle(y_start)
        sleep(0.5)
        while y_start < y_final:
            #Do the reading and compare the voltage to the max readed
            readings = 0
            x.ChangeDutyCycle(x_start)
            sleep(0.5)
            y.ChangeDutyCycle(y_start)
            sleep(0.5)
            if readings > max_voltage:
                x_max = x_start
                y_max = y_start
                voltage = read_voltage()
            y_start+= step
        x_start+=step
    print('Best position:', x_max, y_max)
    #Set position
    x.ChangeDutyCycle(x_max)
    y.ChangeDutyCycle(y_max)
    
    return jsonify({'algo':'puto'})
    
if __name__ == '__main__':
    app.run()
    
