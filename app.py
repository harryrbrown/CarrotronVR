import logging

try:
    import cmath as math
except ImportError:
    import math

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, current_app, render_template
from flask_socketio import SocketIO, send

from Carrotron2.board.arduino import ArduinoBoard
from Carrotron2.control.pilot import DifferentialPilot
from Carrotron2.output import MotorDriveL9110, ServoSG90

logging.basicConfig(level=logging.DEBUG)

MOTOR_A_PINS = (4, 5)
MOTOR_B_PINS = (6, 7)
X_SERVO = (8,)
Y_SERVO = (9,)


board = ArduinoBoard('/dev/ttyACM1')

leftmotor = MotorDriveL9110(board, MOTOR_A_PINS)
rightmotor = MotorDriveL9110(board, MOTOR_B_PINS)
xservo = ServoSG90(board, X_SERVO)
yservo = ServoSG90(board, Y_SERVO)

xservo.set_degrees(90)
yservo.set_degrees(90) # Set the pins to the middle

config = {
    'SECRET_KEY': 'sglkaj;lgkjrfla',

    'ROBOT': {
        'board': board,
        'leftmotor': leftmotor,
        'rightmotor': rightmotor,
        'driver': DifferentialPilot(board, leftmotor, rightmotor),
        'xservo': xservo,
        'yservo': yservo,

        'X_JOYSTICK_SENSATIVITY': 1.0,  # Reduce these to reduce the rotation speed of robot.
        'Y_JOYSTICK_SENSATIVITY': 1.0,
    }
}

app = Flask(__name__)
socket = SocketIO(app)
app.config.from_object(config)


@socket.on('angles')
def new_angles(angles):
    """
    Should receive something like: (x, y)

    x & y should be between -90, 90
    """
    print("New angle. Received: {}".format(angles))

    x, y = angles

    app = current_app._get_current_object()
    print(app.config)
    app.config['ROBOT']['xservo'].set_degrees(x + 90)  # Servo wants between 0-180. we get -90 - 90
    app.config['ROBOT']['yservo'].set_degrees(y + 90)
#    send(angles)


@socket.on('joystick')
def new_joystick(data):
    """
    Input should be:
        {
          'joystick0x': ... # range 0-1
          'joystick0y': ... # range 0-1
        }
    """

    joystick_x = data['joystick0x']
    joystick_y = data['joystick0y']

    left_speed = 0
    right_speed = 0

    if joystick_x > 0:
        if joystick_y > 0:
            right_speed = joystick_y
        else:
            right_speed = -joystick_y
        left_speed = (joystick_x ** 2 + joystick_y ** 2) ** 0.5
    else:
        if joystick_y > 0:
            left_speed = joystick_y
        else:
            left_speed = -joystick_y
        right_speed = (joystick_x ** 2 + joystick_y ** 2) ** 0.5

    with current_app as app:
        app.config['ROBOT']['leftmotor'].set_speed(left_speed)
        app.config['ROBOT']['rightmotor'].set_speed(right_speed)


@app.route('/')
def index():
    return render_template('videofeed.html')


if __name__ == '__main__':
    context = ('selfsign.crt', 'selfsign.key')
    socket.run(app, host='0.0.0.0', port=5000, debug=True, ssl_context=context)
