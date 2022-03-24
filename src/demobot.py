import time

from lib.libwallaby import libwallaby
from lib.wheels import *

red_channel = 0
green_channel = 1

arm_servo = Servo(port=0, delay=20)

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

def main():
    libwallaby.camera_open()

    # TODO: Get in position

    colors = []

    def collect_poms():
        lower_arm()

        for _ in range(3):
            color = collect_pom()

            if color:
                colors.append(color)

        raise_arm()

    with_reset_wheels(collect_poms, padding=cm(5))

    print("COLORS:", colors)

def raise_arm():
    arm_servo.set(370)

def lower_arm():
    arm_servo.set(540)

def collect_pom():
    for _ in range(10):
        libwallaby.camera_update()

    left_velocity = calculate_velocity(wheels.left_motor.speed, Direction.forward, wheels.left_offset)
    right_velocity = calculate_velocity(wheels.right_motor.speed, Direction.forward, wheels.right_offset)

    libwallaby.move_at_velocity(wheels.left_motor.port, left_velocity)
    libwallaby.move_at_velocity(wheels.right_motor.port, right_velocity)

    libwallaby.motor(spinner_motor.port, 100)

    timeout = 3

    start = time.time()
    while True:
        libwallaby.camera_update()

        if libwallaby.get_object_count(red_channel) > 0 or libwallaby.get_object_count(green_channel) > 0 or time.time() - start > timeout:
            break

    wheels.force_stop()

    wheels.drive(Direction.forward, cm(10))

    # Keep trying to pull in the pom pom until it's secured in the shaft
    color = None
    start = time.time()
    while True:
        libwallaby.camera_update()

        if libwallaby.get_object_count(red_channel) > 0:
            color = Color.red
        elif libwallaby.get_object_count(green_channel) > 0:
            color = Color.green
        elif color or time.time() - start > timeout:
            break

    libwallaby.off(spinner_motor.port)

    return color

def with_reset_wheels(f, padding = 0):
    initial_position_left = libwallaby.get_motor_position_counter(wheels.left_motor.port)
    initial_position_right = libwallaby.get_motor_position_counter(wheels.right_motor.port)

    f()

    final_position_left = libwallaby.get_motor_position_counter(wheels.left_motor.port)
    final_position_right = libwallaby.get_motor_position_counter(wheels.right_motor.port)

    left_distance = final_position_left - initial_position_left
    right_distance = final_position_right - initial_position_right

    distance = (left_distance if left_distance < right_distance else right_distance) / motor_pwm_ticks / motor_travel_time_1_cm

    wheels.drive(Direction.reverse, distance - padding)
