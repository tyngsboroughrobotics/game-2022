#ifndef WHEELS_H_
#define WHEELS_H_

#define MOTOR_PWM_TICKS 1500.0
#define MOTOR_TRAVEL_TIME_1_CM 0.0625

#define M(x) ((x) / 100.0)
#define CM(x) (x)
#define MM(x) ((x) * 10.0)
#define IN(x) ((x) * 2.54)

typedef double Duration;

typedef enum {
    FORWARD = 0,
    REVERSE = 1,
} DriveDirection;

typedef enum {
    LEFT = 0,
    RIGHT = 1,
} TurnDirection;

double scale(double n, double in_min, double in_max, double out_min, double out_max);

typedef struct {
    int port;
    double speed;
} Motor;

void drive_motor(Motor motor, DriveDirection direction, double cm);

void force_stop_motor(Motor motor);

Duration motor_block_duration(double cm, int velocity);

typedef struct {
    Motor left_motor;
    Motor right_motor;
    double left_offset;
    double right_offset;
} Wheels;

void drive_wheels(Wheels wheels, DriveDirection direction, double cm);

void turn_wheels(Wheels wheels, TurnDirection direction, double deg);

void drive_in_unison(Wheels wheels, int left_velocity, int right_velocity, Duration sleep_time);

void force_stop_wheels(Wheels wheels);

int calculate_velocity(double speed, DriveDirection direction, double offset);

double wheels_turn_amount(double degrees);

typedef struct {
    int port;
} Servo;

void set_servo(Servo servo, int position);

#endif /* WHEELS_H_ */
