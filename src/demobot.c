#if __has_include(<kipr/wombat.h>)
#include <kipr/wombat.h>
#else
#error "Please compile on the Wombat"
#endif

#include <stdio.h>
#include <stdlib.h>
#include "wheels.h"

void collect_pom(TurnDirection direction);
void raise_plow();
void lower_plow();
Motor plow_motor_for_direction(TurnDirection direction);

const int red_channel = 0;
const int green_channel = 1;

const Servo plow_servo = {
    .port = 0,
};

const Motor plow_left = {
    .port = 2,
    .speed = 1.0,
};

const Motor plow_right = {
    .port = 3,
    .speed = 1.0,
};

const Wheels wheels = {
    .left_motor = {
        .port = 0,
        .speed = 1.0,
    },
    .right_motor = {
        .port = 1,
        .speed = 1.0,
    },
    .left_offset = 1.25,
    .right_offset = 1.0,
};

int main() {
    // lower_plow();
    collect_pom(RIGHT);

    // motor(plow_left.port, 100);
    // msleep(5000);
    // off(plow_left.port);

    return 0;

    camera_open();

    lower_plow();

    for (int i = 0; i < 1; i++) {
        for (int i = 0; i < 10; i++) {
            camera_update();
        }

        if (get_object_count(red_channel) > 0) {
            // Red pom
            printf("Red!\n"); fflush(stdout);
            collect_pom(LEFT);
        } else {
            // Green pom
            printf("Green!\n"); fflush(stdout);
            collect_pom(RIGHT);
        }

        drive_wheels(wheels, FORWARD, IN(6));

        msleep(2000); // FIXME: TEMPORARY
    }

    raise_plow();

    camera_close();

    return 0;
}

void collect_pom(TurnDirection direction) {
    const double turn_amount = 30.0;
    const double drive_amount = IN(6.0);

    Motor plow_motor = plow_motor_for_direction(direction);

    // Turn to collect the poms
    motor(plow_motor.port, 100);
    turn_wheels(wheels, direction, turn_amount);
    drive_wheels(wheels, FORWARD, drive_amount);

    // Get back on track
    drive_wheels(wheels, REVERSE, drive_amount);
    off(plow_motor.port);
    turn_wheels(wheels, !direction, turn_amount);
}

void raise_plow() {
    set_servo(plow_servo, 750);
}

void lower_plow() {
    set_servo(plow_servo, 1000);
}

Motor plow_motor_for_direction(TurnDirection direction) {
    switch (direction) {
    case LEFT:
        return plow_right;
    default:
        return plow_left;
    }
}
