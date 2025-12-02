import lgpio
import time
#https://github.com/jonaw2005/briefkasten_api.git

# PIN ASSIGNMENTS
LED_RED_PIN = 17
LED_YELLOW_PIN = 27
LED_GREEN_PIN = 22
SERVO_PIN = 23
TASTER_PIN = 24
LICHTSCHRANKE_PIN = 25

# GPIO SETUP
h = lgpio.gpiochip_open(0)  # Öffne den GPIO-Chip

# Output Pins setzen
lgpio.gpio_claim_output(h, LED_RED_PIN)
lgpio.gpio_claim_output(h, LED_YELLOW_PIN)
lgpio.gpio_claim_output(h, LED_GREEN_PIN)
lgpio.gpio_claim_output(h, SERVO_PIN)

# Input Pins setzen
lgpio.gpio_claim_input(h, TASTER_PIN)
lgpio.gpio_claim_input(h, LICHTSCHRANKE_PIN)

# SERVO SETUP (PWM) - Wird in den Funktionen initialisiert


def led_red():
    lgpio.gpio_write(h, LED_RED_PIN, 1)

def led_yellow():
    lgpio.gpio_write(h, LED_YELLOW_PIN, 1)

def led_green():
    lgpio.gpio_write(h, LED_GREEN_PIN, 1)

def led_off():
    lgpio.gpio_write(h, LED_RED_PIN, 0)
    lgpio.gpio_write(h, LED_YELLOW_PIN, 0)
    lgpio.gpio_write(h, LED_GREEN_PIN, 0)


def servo_open():
    # 180 Grad: ~2.4ms Puls bei 50Hz (20ms Periode)
    lgpio.tx_pwm(h, SERVO_PIN, 20000, 2400)
    time.sleep(0.5)

def servo_close():
    # 0 Grad: ~0.6ms Puls bei 50Hz (20ms Periode)
    lgpio.tx_pwm(h, SERVO_PIN, 20000, 600)
    time.sleep(0.5)


def taster_callback(chip, gpio, level, tick):
    led_red()

def lichtschranke_callback(chip, gpio, level, tick):
    led_green()


def setup_callbacks():
    lgpio.gpio_claim_alert(h, TASTER_PIN, lgpio.FALLING_EDGE, None)
    lgpio.gpio_claim_alert(h, LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE, None)
    
    lgpio.callback(h, TASTER_PIN, lgpio.FALLING_EDGE, taster_callback)
    lgpio.callback(h, LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE, lichtschranke_callback)


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
    finally:
        lgpio.gpiochip_close(h)

test_callbacks()