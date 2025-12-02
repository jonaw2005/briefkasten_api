import RPi.GPIO as GPIO
import time
#https://github.com/jonaw2005/briefkasten_api.git

# PIN ASSIGNMENTS
LED_RED_PIN = 17
LED_YELLOW_PIN = 27
LED_GREEN_PIN = 22
SERVO_PIN = 23
TASTER_PIN = 24
LICHTSCHRANKE_PIN = 25
#GND_PIN = 5

GPIO.setwarnings(False)


# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED_PIN, GPIO.OUT)
GPIO.setup(LED_YELLOW_PIN, GPIO.OUT)
GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(TASTER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LICHTSCHRANKE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
    led_red()



def lichtschranke_callback():
    led_green()


def setup_callbacks():
    GPIO.remove_event_detect(TASTER_PIN)
    GPIO.remove_event_detect(LICHTSCHRANKE_PIN)

    GPIO.add_event_detect(TASTER_PIN, GPIO.FALLING, callback=lambda channel: taster_callback(), bouncetime=300)
    GPIO.add_event_detect(LICHTSCHRANKE_PIN, GPIO.FALLING, callback=lambda channel: lichtschranke_callback(), bouncetime=300)


# test
def test():
    while True:
        led_red()
        time.sleep(5)
        led_yellow()
        time.sleep(5)
        led_green()
        time.sleep(5)
        led_off()
        time.sleep(5)
        servo_open()
        time.sleep(2)
        servo_close()
        time.sleep(2)

def test_callbacks():
    setup_callbacks()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

test_callbacks()