#include <kipr/wombat.h>

#define BASKET_MOTOR 1
#define BASKET_TOUCH_UP 1
#define DOOR_SERVO 1
#define ARM_SERVO 2 // port 0 is broken

void raise_basket();
void lower_basket();
void raise_arm();
void lower_arm();

int main()
{
    create_connect();
    enable_servos();

    // NOTE: The basket should be started raised
    raise_arm();

    // Drive to the PCR machine door

    // drive straight across the table
    create_drive_direct(500, 500);
    msleep(2500);

    // turn left 90 deg
    create_drive_direct(-500, 500);
    msleep(500);

    // drive toward the PCR machine
    create_drive_direct(500, 500);
    msleep(1300);

    // turn left 90 deg
    create_drive_direct(-500, 500);
    msleep(440);

    // drive parallel to the PCR machine
    create_drive_direct(500, 500);
    msleep(450);

    // turn right 90 deg
    create_drive_direct(500, -500);
    msleep(450);

    // drive up to the door
    create_drive_direct(100, 100);
    msleep(50);

    create_stop();

    // Lift the door

    // approach the door
    lower_basket();
    lower_arm();
    create_drive_direct(100, 100);
    msleep(1050);
    create_stop();

    // lift the door
    raise_arm();

    msleep(2000);

    // TEMPORARY: RESET
    lower_arm();
    create_drive_direct(-100, -100);
    msleep(500);
	create_stop();

    // Reset

	msleep(2000);
    raise_arm();
    raise_basket();

    // Plow the poms

    // turn right 90 degrees
    create_drive_direct(500, -500);
    msleep(500);

    // drive straight toward the end of the table
    create_drive_direct(500, 500);
    msleep(1750);

    create_stop();

    return 0;

    /*

    // I have this commented out in case we need a reset of the basket
    //moveBasketTime(basketMotor, 6000, -100);

    // Sets the door arm and basket up so that the create can move
    moveDoor(doorServo, 1850);
   	if (digital(basketTouchUp) == 0) {
  		moveBasketSensor(basketMotor, basketTouchUp, 100);
    }

    // Drive the create to the PCR machine door


    create_stop();

   // Brings basket back down (keep commented out for now)
   // moveBasketTime(basketMotor, 6000, -100);

    return 0;

    */
}

void raise_basket() {
    while (digital(1) == 0) {
  		motor(BASKET_MOTOR, 60);
    }
    msleep(100);
}

void lower_basket() {
    motor(BASKET_MOTOR, -100);
    msleep(5000);
}

void raise_arm() {
    set_servo_position(ARM_SERVO, 2000);
    msleep(500);
}

void lower_arm() {
    set_servo_position(ARM_SERVO, 700);
    msleep(500);
}

/*

int moveBasketSensor(int mPort, int dPort, int percentSpeed)
{
	while (digital(dPort) == 0) {
        motor(mPort, percentSpeed);
    }
    ao();
    return 0;
}

int moveBasketTime(int mPort, int time, int percentSpeed)
{
	motor(mPort, percentSpeed);
    msleep(time);
    ao();
    return 0;
}

int moveDoor(int sPort, int servoPosition)
{
    enable_servos();
    set_servo_position(sPort, servoPosition);
    return 0;
}
*/
