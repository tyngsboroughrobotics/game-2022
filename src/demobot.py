import sys

from lib.libwallaby import libwallaby
from lib.wheels import *

red_channel = 0
green_channel = 1

arm_servo = Servo(port=0)
splitter_servo = Servo(port=1)

spinner_motor = Motor(port=2, speed=1)

wheels = Wheels(
    left_motor=Motor(port=0, speed=1),
    right_motor=Motor(port=1, speed=1),
    left_offset=0.9975, # if <1, veers to the right
    right_offset=1.0 # if <1, veers to the left
)

class Color(Enum):
    red = 0
    green = 1

# lift arm
#
# repeat 8 times:
#     if green:
#         move servo left
#     else:
#         move servo right
#     move forward
#
# lower arm
#
# THEN: go back around to collect poms

def main():
    libwallaby.camera_open()
    raise_arm()
    # reset_splitter()

    # initial_position_left = libwallaby.get_motor_position_counter(wheels.left_motor.port)
    # initial_position_right = libwallaby.get_motor_position_counter(wheels.right_motor.port)

    colors = []

    lower_arm()
    enable_spinner()

    for _ in range(3):
        drive_until_reached_pom()

        pom_is_red = libwallaby.get_object_count(red_channel) > 0
        advance_distance = cm(12)

        if pom_is_red:
            print("Red!"); sys.stdout.flush()
            colors.append(Color.red)
        else:
            print("Green!"); sys.stdout.flush()
            colors.append(Color.green)

        wheels.drive(Direction.forward, advance_distance)

    disable_spinner()
    raise_arm()

    print("COLORS:", colors)

def raise_arm():
    arm_servo.set(1260)

def lower_arm():
    arm_servo.set(1460)

def enable_spinner():
    libwallaby.motor(spinner_motor.port, 100)

def disable_spinner():
    libwallaby.off(spinner_motor.port)

def drive_until_reached_pom():
    for _ in range(10):
        libwallaby.camera_update()

    left_velocity = calculate_velocity(wheels.left_motor.speed, Direction.forward, wheels.left_offset)
    right_velocity = calculate_velocity(wheels.right_motor.speed, Direction.forward, wheels.right_offset)

    libwallaby.move_at_velocity(wheels.left_motor.port, left_velocity)
    libwallaby.move_at_velocity(wheels.right_motor.port, right_velocity)

    while True:
        libwallaby.camera_update()

        if libwallaby.get_object_count(red_channel) > 0 or libwallaby.get_object_count(green_channel) > 0:
            break

    wheels.force_stop()
