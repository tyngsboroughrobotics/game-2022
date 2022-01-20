#include <kipr/wombat.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include "wheels.h"

#define RED_CHANNEL 0
#define GREEN_CHANNEL 1

void collect_poms(Wheels wheels, TurnDirection direction);

int main() {
    Wheels wheels = {
        .left_motor = {
            .port = 0,
            .speed = 1.0,
        },
        .right_motor = {
            .port = 1,
            .speed = 1.0,
        },
        .left_offset = 0.975,
        .right_offset = 1.0,
    };

    camera_open();

    for (int i = 0; i < 4; i++) {
        drive_wheels(wheels, FORWARD, IN(6));

        for (int i = 0; i < 10; i++) {
            camera_update();
        }

        if (get_object_count(RED_CHANNEL) > 0) {
            // Red pom
            printf("Red!\n"); fflush(stdout);
            collect_poms(wheels, LEFT);
        } else {
            // Green pom
            printf("Green!\n"); fflush(stdout);
            collect_poms(wheels, RIGHT);
        }

        msleep(2000);
    }

    camera_close();

    return 0;
}

void collect_poms(Wheels wheels, TurnDirection direction) {
    const double turn_amount = 30.0;
    const double drive_amount = CM(10.0);

    // Turn to collect the poms
    turn_wheels(wheels, direction, turn_amount);
    drive_wheels(wheels, FORWARD, drive_amount);

    // Get back on track
    turn_wheels(wheels, !direction, turn_amount * 2);
    drive_wheels(wheels, FORWARD, drive_amount);
    turn_wheels(wheels, direction, turn_amount);
}
