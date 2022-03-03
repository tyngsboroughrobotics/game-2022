#include <stdlib.h>
#include <kipr/wombat.h>
#include "wheels.h"

double scale(double n, double in_min, double in_max, double out_min, double out_max) {
    return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void drive_motor(Motor motor, DriveDirection direction, double cm) {
    int velocity = motor.speed * MOTOR_PWM_TICKS;

    if (direction == REVERSE) {
        velocity *= -1;
    }

    move_at_velocity(motor.port, velocity);

    Duration block_duration = motor_block_duration(cm, velocity);

    msleep((int) block_duration);

    force_stop_motor(motor);
}

void force_stop_motor(Motor motor) {
    move_at_velocity(motor.port, 0);
    msleep(50);
    off(motor.port);
}

Duration motor_block_duration(double cm, int velocity) {
    return fabs(MOTOR_PWM_TICKS * MOTOR_TRAVEL_TIME_1_CM * cm / (double) velocity) * 1000.0;
}

void drive_wheels(Wheels wheels, DriveDirection direction, double cm) {
    int left_velocity = calculate_velocity(wheels.left_motor.speed, direction, wheels.left_offset);
    int right_velocity = calculate_velocity(wheels.right_motor.speed, direction, wheels.right_offset);

    int slower_velocity = left_velocity < right_velocity ? left_velocity : right_velocity;
    int sleep_time = motor_block_duration(cm, slower_velocity);

    drive_in_unison(wheels, left_velocity, right_velocity, sleep_time);
}

void turn_wheels(Wheels wheels, TurnDirection direction, double deg) {
    DriveDirection left_direction;
    DriveDirection right_direction;

    if (direction == LEFT) {
        left_direction = REVERSE;
        right_direction = FORWARD;
    } else {
        left_direction = FORWARD;
        right_direction = REVERSE;
    }

    int left_velocity = calculate_velocity(wheels.left_motor.speed, left_direction, wheels.left_offset);
    int right_velocity = calculate_velocity(wheels.right_motor.speed, right_direction, wheels.right_offset);

    double cm = wheels_turn_amount(deg);
    Duration sleep_time = motor_block_duration(cm, left_velocity);

    drive_in_unison(wheels, left_velocity, right_velocity, sleep_time);
}

void drive_in_unison(Wheels wheels, int left_velocity, int right_velocity, Duration sleep_time) {
    move_at_velocity(wheels.left_motor.port, left_velocity);
    move_at_velocity(wheels.right_motor.port, right_velocity);

    msleep(sleep_time);

    force_stop_wheels(wheels);
}

void force_stop_wheels(Wheels wheels) {
    move_at_velocity(wheels.left_motor.port, 0);
    move_at_velocity(wheels.right_motor.port, 0);
    msleep(50);
    off(wheels.left_motor.port);
    off(wheels.right_motor.port);
}

int calculate_velocity(double speed, DriveDirection direction, double offset) {
    int velocity = (int) (speed * MOTOR_PWM_TICKS * offset);

    if (direction == REVERSE) {
        velocity *= -1;
    }

    return velocity;
}

double wheels_turn_amount(double degrees) {
    int multiplier;

    if (degrees == 45) {
        multiplier = 1.175;
    } else if (degrees == 90) {
        multiplier = 1.2425;
    } else if (degrees == 180) {
        multiplier = 1.35;
    } else if (degrees == 360) {
        multiplier = 1.425;
    } else {
        multiplier =
            -2.781096509 * powf(10.0, -6.0) * powf(degrees, 2.0)
                + 1.922759857 * powf(10.0, -3.0) * degrees
                + 1.093333333;
    }

    return degrees * multiplier / 10.0;
}

void set_servo(Servo servo, int position) {
    enable_servos();
    set_servo_position(servo.port, position);
    msleep(750);
}
