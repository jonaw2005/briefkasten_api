import RPi.GPIO as GPIO

# PIN ASSIGNMENTS
LED_RED_PIN = 17
LED_YELLOW_PIN = 27
LED_GREEN_PIN = 22
SERVO_PIN = 23
#GND_PIN = 5


GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED_PIN, GPIO.OUT)
GPIO.setup(LED_YELLOW_PIN, GPIO.OUT)
GPIO.setup(LED_GREEN_PIN, GPIO.OUT)




def led_red():
    GPIO.output(LED_RED_PIN, GPIO.HIGH)

def led_yellow():
    GPIO.output(LED_YELLOW_PIN, GPIO.HIGH)

def led_green():
    GPIO.output(LED_GREEN_PIN, GPIO.HIGH)

def led_off():
    GPIO.output(LED_RED_PIN, GPIO.LOW)
    GPIO.output(LED_YELLOW_PIN, GPIO.LOW)
    GPIO.output(LED_GREEN_PIN, GPIO.LOW)


def servo_open():
    pass


def servo_close():
    pass


