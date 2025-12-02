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


def send_servo_pulse(pulse_us, duration_s=0.5, period_us=20000):
    """Sende software-gesteuerte PWM-Pulse (pulse_us in µs) für duration_s Sekunden."""
    end = time.time() + duration_s
    while time.time() < end:
        lgpio.gpio_write(h, SERVO_PIN, 1)
        time.sleep(pulse_us / 1_000_000.0)
        lgpio.gpio_write(h, SERVO_PIN, 0)
        time.sleep((period_us - pulse_us) / 1_000_000.0)
    # sicherstellen, dass Pin am Ende low ist
    lgpio.gpio_write(h, SERVO_PIN, 0)

def servo_open():
    # ~2.4ms Puls für Richtung "offen"
    send_servo_pulse(2400, duration_s=0.6)

def servo_close():
    # ~0.6ms Puls für Richtung "geschlossen"
    send_servo_pulse(600, duration_s=0.6)


def taster_callback(chip, gpio, level, tick):
    print("Taster gedrückt!")
    led_red()

def lichtschranke_callback(chip, gpio, level, tick):
    print("Lichtschranke unterbrochen!")
    led_green()


def setup_callbacks():
    lgpio.gpio_claim_alert(h, TASTER_PIN, lgpio.FALLING_EDGE)
    lgpio.gpio_claim_alert(h, LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE)
    
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

#test_callbacks()
test()