import RPi.GPIO as GPIO
import time


# PIN ASSIGNMENTS
LED_RED_PIN = 17
LED_YELLOW_PIN = 27
LED_GREEN_PIN = 22
SERVO_PIN = 23
TASTER_PIN = 24
LICHTSCHRANKE_PIN = 25
#GND_PIN = 5


# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED_PIN, GPIO.OUT)
GPIO.setup(LED_YELLOW_PIN, GPIO.OUT)
GPIO.setup(LED_GREEN_PIN, GPIO.OUT)


# SERVO SETUP
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz Frequenz für Standard-Servos
servo_pwm.start(0)



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
    # 180 Grad: Duty Cycle ~12%
    servo_pwm.ChangeDutyCycle(12)
    time.sleep(0.5)

def servo_close():
    # 0 Grad: Duty Cycle ~3%
    servo_pwm.ChangeDutyCycle(3)
    time.sleep(0.5)


def taster_callback():
    pass



def lichtschranke_callback():
    pass



