from enum import Enum
import math
import sys

from .libwallaby import libwallaby

motor_pwm_ticks = 1500
motor_travel_time_1_cm = 0.0625


def m(x):
    return x * 100


def cm(x):
    return x


def mm(x):
    return x / 10


def inches(x):
    return x * 2.54


class Direction(Enum):
    forward = 0
    reverse = 1

    def toggle(self):
        return Direction.reverse if self == Direction.forward else Direction.forward


class TurnDirection(Enum):
    left = 0
    right = 1

    def toggle(self):
        return TurnDirection.right if self == TurnDirection.left else TurnDirection.left


def scale(n, in_min, in_max, out_min, out_max):
    return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Motor:
    def __init__(self, port, speed):
        self.port = port
        self.speed = speed

    def drive(self, direction, cm):
        velocity = int(self.speed * motor_pwm_ticks)

        if direction == Direction.reverse:
            velocity *= -1

        libwallaby.move_at_velocity(self.port, velocity)

        block_duration = motor_block_duration(cm, velocity)

        libwallaby.msleep(int(block_duration))

        self.stop()

    def start(self, direction):
        velocity = int(self.speed * motor_pwm_ticks)

        if direction == Direction.reverse:
            velocity *= -1

        libwallaby.move_at_velocity(self.port, velocity)

    def stop(self):
        libwallaby.move_at_velocity(self.port, 0)
        libwallaby.msleep(50)
        libwallaby.off(self.port)


def motor_block_duration(cm, velocity):
    return int(abs(motor_pwm_ticks * motor_travel_time_1_cm * cm / velocity) * 1000)


class Wheels:
    def __init__(self, left_motor, right_motor, left_offset=1, right_offset=1):
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.left_offset = left_offset
        self.right_offset = right_offset

    def drive(self, direction, cm):
        left_velocity = calculate_velocity(
            self.left_motor.speed, direction, self.left_offset
        )
        right_velocity = calculate_velocity(
            self.right_motor.speed, direction, self.right_offset
        )

        slower_velocity = (
            left_velocity if left_velocity < right_velocity else right_velocity
        )
        sleep_time = motor_block_duration(cm, slower_velocity)

        self.drive_in_unison(left_velocity, right_velocity, sleep_time)

    def start_turn(self, direction):
        if direction == TurnDirection.left:
            left_direction = Direction.forward
            right_direction = Direction.reverse
        else:
            left_direction = Direction.reverse
            right_direction = Direction.forward

        left_velocity = calculate_velocity(
            self.left_motor.speed, left_direction, self.left_offset
        )
        right_velocity = calculate_velocity(
            self.right_motor.speed, right_direction, self.right_offset
        )

        libwallaby.move_at_velocity(self.left_motor.port, left_velocity)
        libwallaby.move_at_velocity(self.right_motor.port, right_velocity)

    def turn(self, direction, deg):
        if direction == TurnDirection.left:
            left_direction = Direction.forward
            right_direction = Direction.reverse
        else:
            left_direction = Direction.reverse
            right_direction = Direction.forward

        left_velocity = calculate_velocity(
            self.left_motor.speed, left_direction, self.left_offset
        )
        right_velocity = calculate_velocity(
            self.right_motor.speed, right_direction, self.right_offset
        )

        cm = wheels_turn_amount(deg)
        sleep_time = motor_block_duration(cm, left_velocity)

        self.drive_in_unison(left_velocity, right_velocity, sleep_time)

    def drive_in_unison(self, left_velocity, right_velocity, sleep_time):
        libwallaby.move_at_velocity(self.left_motor.port, left_velocity)
        libwallaby.move_at_velocity(self.right_motor.port, right_velocity)

        libwallaby.msleep(sleep_time)

        self.stop()

    def start(self, direction):
        left_velocity = calculate_velocity(
            self.left_motor.speed, direction, self.left_offset
        )

        right_velocity = calculate_velocity(
            self.right_motor.speed, direction, self.right_offset
        )

        libwallaby.move_at_velocity(self.left_motor.port, left_velocity)
        libwallaby.move_at_velocity(self.right_motor.port, right_velocity)

    def stop(self):
        libwallaby.move_at_velocity(self.left_motor.port, 0)
        libwallaby.move_at_velocity(self.right_motor.port, 0)
        libwallaby.msleep(50)
        libwallaby.off(self.left_motor.port)
        libwallaby.off(self.right_motor.port)


def calculate_velocity(speed, direction, offset):
    velocity = int(speed * motor_pwm_ticks * offset)

    if direction == Direction.reverse:
        velocity *= -1

    return velocity


def wheels_turn_amount(degrees):
    if degrees == 45:
        multiplier = 1.175
    elif degrees == 90:
        multiplier = 1.2425
    elif degrees == 180:
        multiplier = 1.35
    elif degrees == 360:
        multiplier == 1.425
    else:
        multiplier = (
            -2.781096509 * 10.0**-6.0 * degrees**2.0
            + 1.922759857 * 10.0**-3.0 * degrees
            + 1.093333333
        )

    return degrees * multiplier / 10


class Servo:
    def __init__(self, port, delay):
        self.port = port
        self.delay = delay

    def set(self, target_position):
        assert self.delay > 0

        libwallaby.enable_servos()

        position = libwallaby.get_servo_position(self.port)
        sign = int(math.copysign(1, target_position - position))
        increment = 5 * sign

        while abs(position - target_position) >= 5:
            position += increment
            libwallaby.set_servo_position(self.port, position)
            libwallaby.msleep(self.delay)
