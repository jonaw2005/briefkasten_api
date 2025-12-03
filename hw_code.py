import lgpio
import time
import datetime
import requests

class BriefkastenHW:
    """Singleton-Klasse für Briefkasten Hardware-Steuerung"""
    _instance = None
    open = False
    taster = False # False = geschlossen
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BriefkastenHW, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        print("hw initializing...")

        self.serial_number = "SN987654"
        self.api = "http://localhost:5000"


        # PIN ASSIGNMENTS
        self.LED_RED_PIN = 17
        self.LED_YELLOW_PIN = 27
        self.LED_GREEN_PIN = 22
        self.SERVO_PIN = 23
        self.TASTER_PIN = 24
        self.LICHTSCHRANKE_PIN = 25
        
        # GPIO SETUP
        self.h = lgpio.gpiochip_open(0)
        
        # Output Pins setzen
        lgpio.gpio_claim_output(self.h, self.LED_RED_PIN)
        lgpio.gpio_claim_output(self.h, self.LED_YELLOW_PIN)
        lgpio.gpio_claim_output(self.h, self.LED_GREEN_PIN)
        lgpio.gpio_claim_output(self.h, self.SERVO_PIN)
        
        # Input Pins setzen
        lgpio.gpio_claim_input(self.h, self.TASTER_PIN)
        lgpio.gpio_claim_input(self.h, self.LICHTSCHRANKE_PIN)
        
        self.setup_callbacks()
        #self.servo_open()
        time.sleep(1)
        self.servo_close()
        self._initialized = True
    
    def led_red(self):
        lgpio.gpio_write(self.h, self.LED_RED_PIN, 1)
    
    def led_yellow(self):
        lgpio.gpio_write(self.h, self.LED_YELLOW_PIN, 1)
    
    def led_green(self):
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1)
    
    def led_off(self):
        lgpio.gpio_write(self.h, self.LED_RED_PIN, 0)
        lgpio.gpio_write(self.h, self.LED_YELLOW_PIN, 0)
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
    
    def send_servo_pulse(self, pulse_us, duration_s=0.5, period_us=20000):
        """Sende software-gesteuerte PWM-Pulse"""
        end = time.time() + duration_s
        while time.time() < end:
            lgpio.gpio_write(self.h, self.SERVO_PIN, 1)
            time.sleep(pulse_us / 1_000_000.0)
            lgpio.gpio_write(self.h, self.SERVO_PIN, 0)
            time.sleep((period_us - pulse_us) / 1_000_000.0)
        lgpio.gpio_write(self.h, self.SERVO_PIN, 0)
    
    def servo_open(self):
        self.open = True
        self.send_servo_pulse(1400, duration_s=0.6)
    
    def servo_close(self):
        self.open = False
        self.send_servo_pulse(500, duration_s=0.6)
    
    def taster_offen_callback(self, chip, gpio, level, tick):
        print("Taster gedrückt!")
        self.klappe_geoeffnet()
        self.led_red()

    def taster_geschlossen_callback(self, chip, gpio, level, tick):
        print("Taster losgelassen!")
        self.servo_close()
        self.led_off()
    
    def lichtschranke_callback(self, chip, gpio, level, tick):
        print("Lichtschranke unterbrochen!")
        self.led_green()
        self.brief_eingeworfen()
        time.sleep(2)
        self.led_off()

    def taster_edge_callback(self, chip, gpio, level, tick):
        if level == 0:
            self.taster = False
            print("Taster losgelassen!")
            self.taster_offen_callback(chip, gpio, level, tick)
        elif level == 1:
            self.taster = True
            print("Taster gedrückt!")
            self.taster_geschlossen_callback(chip, gpio, level, tick)
    
    def setup_callbacks(self):
        #lgpio.gpio_claim_alert(self.h, self.TASTER_PIN, lgpio.EITHER_EDGE)
        lgpio.gpio_claim_alert(self.h, self.LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE)
        
        

        #lgpio.callback(self.h, self.TASTER_PIN, lgpio.FALLING_EDGE, self.taster_offen_callback)
        lgpio.callback(self.h, self.LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE, self.lichtschranke_callback)

        #lgpio.callback(self.h, self.TASTER_PIN, lgpio.EITHER_EDGE, self.taster_edge_callback)
        #lgpio.gpio_claim_alert(self.h, self.TASTER_PIN, lgpio.RISING_EDGE)
        #lgpio.callback(self.h, self.TASTER_PIN, lgpio.RISING_EDGE, self.taster_geschlossen_callback)

        lgpio.gpio_claim_alert(self.h, self.TASTER_PIN, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.h, self.TASTER_PIN, lgpio.FALLING_EDGE)

        lgpio.callback(self.h, self.TASTER_PIN, lgpio.RISING_EDGE, lambda c, g, l, t: self.taster_edge_callback(c, g, 0, t))
        lgpio.callback(self.h, self.TASTER_PIN, lgpio.FALLING_EDGE, lambda c, g, l, t: self.taster_edge_callback(c, g, 1, t))
        print("Callbacks eingerichtet.")
    def test(self):
        while True:
            self.led_red()
            time.sleep(5)
            self.led_yellow()
            time.sleep(5)
            self.led_green()
            time.sleep(5)
            self.led_off()
            time.sleep(5)
            self.servo_open()
            time.sleep(2)
            self.servo_close()
            time.sleep(2)
    
    def test_callbacks(self):
        self.setup_callbacks()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            lgpio.gpiochip_close(self.h)
    
    def cleanup(self):
        lgpio.gpiochip_close(self.h)


    def brief_eingeworfen(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        response = requests.post(f"{self.api}/new_letter", json={"serial_number": self.serial_number, "time": timestamp})
        print("Brief eingeworfen:", response.json())
        return response.json()

    def klappe_geoeffnet(self):
        print("Klappe wurde geöffnet.")
        return

# Globale Instanz
hw = BriefkastenHW()