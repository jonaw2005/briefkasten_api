import lgpio
import time
import datetime
import requests

# BriefkastenHW kapselt GPIO- und API-Interaktionen für den Briefkasten.
# - steuert LEDs und Servo
# - verarbeitet Taster- und Lichtschranken-Events
# - kommuniziert mit einer HTTP-API (z.B. um Briefe zu melden)

class BriefkastenHW:
    """Singleton-Klasse für Briefkasten Hardware-Steuerung"""
    _instance = None
    open = False
    taster = False # False = geschlossen
    
    def __new__(cls):
        # Singleton-Pattern: eine Instanz pro Laufzeit
        if cls._instance is None:
            cls._instance = super(BriefkastenHW, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Initialisierung nur einmal ausführen
        if self._initialized:
            return
        
        print("hw initializing...")

        # Gerätekennung und API-URL (lokal, zum Testen)
        self.serial_number = "SN987654"
        self.api = "http://localhost:5000"


        # PIN ASSIGNMENTS - BCM-Nummern
        self.LED_RED_PIN = 17
        self.LED_YELLOW_PIN = 27
        self.LED_GREEN_PIN = 22
        self.SERVO_PIN = 23
        self.TASTER_PIN = 24
        self.LICHTSCHRANKE_PIN = 25
        
        # GPIO SETUP - öffne gpiochip und beanspruche Pins
        self.h = lgpio.gpiochip_open(0)
        
        # Output Pins als Ausgänge deklarieren (LEDs + Servo Steuerpin)
        lgpio.gpio_claim_output(self.h, self.LED_RED_PIN)
        lgpio.gpio_claim_output(self.h, self.LED_YELLOW_PIN)
        lgpio.gpio_claim_output(self.h, self.LED_GREEN_PIN)
        lgpio.gpio_claim_output(self.h, self.SERVO_PIN)
        
        # Input Pins setzen: Taster mit Pull-Down, Lichtschranke ohne Extra-Pull
        lgpio.gpio_claim_input(self.h, self.TASTER_PIN, lgpio.SET_PULL_DOWN)
        lgpio.gpio_claim_input(self.h, self.LICHTSCHRANKE_PIN)
        # Callback-Registrierung (siehe setup_callbacks)
        self.setup_callbacks()

        # Initialbewegung des Servos: kurz öffnen -> schließen, als Selbsttest
        time.sleep(1)
        self.servo_close()
        # Gelbe LED als "in Betrieb"-Anzeige
        self.led_yellow()
        # Teste API-Verbindung, bei Fehler LED-Rot einschalten
        if not self.test_connection():
            self.led_off()
            self.led_red()
        self._initialized = True
    
    # LED-Kurzfunktionen: schreiben einfach 0/1 auf die Pins
    def led_red(self):
        lgpio.gpio_write(self.h, self.LED_RED_PIN, 1)
    
    def led_yellow(self):
        lgpio.gpio_write(self.h, self.LED_YELLOW_PIN, 1)
    
    def led_green(self):
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1)
    
    def led_off(self):
        # Alle LEDs ausschalten
        lgpio.gpio_write(self.h, self.LED_RED_PIN, 0)
        lgpio.gpio_write(self.h, self.LED_YELLOW_PIN, 0)
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
    
    def send_servo_pulse(self, pulse_us, duration_s=0.5, period_us=20000):
        """Sende software-gesteuerte PWM-Pulse.
        
        pulse_us: Pulsbreite in Mikrosekunden (z.B. 600..2400)
        duration_s: wie lange die Pulsfolge gesendet wird
        period_us: Periode des Servosignals (typisch 20000µs = 20ms = 50Hz)
        """
        end = time.time() + duration_s
        while time.time() < end:
            lgpio.gpio_write(self.h, self.SERVO_PIN, 1)
            time.sleep(pulse_us / 1_000_000.0)                     # High-Zeit
            lgpio.gpio_write(self.h, self.SERVO_PIN, 0)
            time.sleep((period_us - pulse_us) / 1_000_000.0)       # Rest der Periode
        # Sicherstellen, dass Pin am Ende Low ist
        lgpio.gpio_write(self.h, self.SERVO_PIN, 0)
    
    def servo_open(self):
        """Bewege Servo in die 'offen'-Position (Pulse-Wert anpassen falls nötig)."""
        self.open = True
        # 1400µs ist ein Testwert; kalibrieren auf dein Servo
        self.send_servo_pulse(1400, duration_s=0.6)
    
    def servo_close(self):
        """Bewege Servo in die 'geschlossen'-Position (Pulse-Wert anpassen falls nötig)."""
        self.open = False
        # 500µs ist ein Testwert; kalibrieren auf dein Servo
        self.send_servo_pulse(500, duration_s=0.6)
    
    # Callback-Funktionen für Taster/Lichtschranke:
    # Diese Funktionen werden von lgpio aufgerufen, wenn ein Event eintrifft.
    def taster_offen_callback(self, chip, gpio, level, tick):
        """Handler für 'Taster offen' (z.B. losgelassen)."""
        print("Taster gedrückt!")
        self.klappe_geoeffnet()
        self.servo_close()
        # Informiere API, dass Klappe geschlossen ist (Endpoint '/closed' erwartet)
        response = requests.post(f"{self.api}/closed", json={"serial_number": self.serial_number})

    def taster_geschlossen_callback(self, chip, gpio, level, tick):
        """Handler für 'Taster geschlossen' (z.B. gedrückt)."""
        print("Taster losgelassen!")
        self.servo_open()
        self.led_off()
        self.led_yellow()
        # Informiere API, dass Klappe offen ist (Endpoint '/open' erwartet)
        response = requests.post(f"{self.api}/open", json={"serial_number": self.serial_number})
    
    def lichtschranke_callback(self, chip, gpio, level, tick):
        """Handler für Lichtschranke-Unterbrechung (Briefwurf erkannt)."""
        print("Lichtschranke unterbrochen!")
        self.led_green()
        self.brief_eingeworfen()
        # kurze Anzeigezeit, danach ggf. ausschalten
        time.sleep(2)
        #self.led_off()

    def taster_edge_callback(self, chip, gpio, level, tick):
        """Gemeinsamer Edge-Handler: level==1 -> gedrückt, level==0 -> losgelassen.
        
        Leitet an die spezifischen Handler weiter.
        """
        if level == 1:
            self.taster = True
            print("Taster gedrückt!")
            self.taster_geschlossen_callback(chip, gpio, level, tick)
        else:
            self.taster = False
            print("Taster losgelassen!")
            self.taster_offen_callback(chip, gpio, level, tick)
    
    def setup_callbacks(self):
        """Registriert die benötigten Alerts/Callbacks bei lgpio.

        - Lichtschranke: FALLING_EDGE (Unterbrechung)
        - Taster: BOTH_EDGES (sorgt dafür, dass sowohl drücken als auch loslassen erkannt werden)
        """
        # Lichtschranke bei FALLING_EDGE registrieren
        lgpio.gpio_claim_alert(self.h, self.LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE)
        
        # Callback für Lichtschranke setzen (führt lichtschranke_callback aus)
        lgpio.callback(self.h, self.LICHTSCHRANKE_PIN, lgpio.FALLING_EDGE, self.lichtschranke_callback)

        # Taster: BOTH_EDGES verwenden, damit sowohl FALLING als auch RISING erkannt werden.
        # Der Callback ruft taster_edge_callback mit dem übergebenen level auf.
        lgpio.gpio_claim_alert(self.h, self.TASTER_PIN, lgpio.BOTH_EDGES)
        lgpio.callback(self.h, self.TASTER_PIN, lgpio.BOTH_EDGES, lambda c, g, l, t: self.taster_edge_callback(c, g, l, t))
        print("Callbacks eingerichtet.")
    
    def test(self):
        """Einfacher Test-Loop, der LEDs und Servo zyklisch bewegt (für manuelle Tests)."""
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
        """Startet die Callback-Registrierung und hält das Programm am Leben, damit Callbacks laufen."""
        self.setup_callbacks()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            lgpio.gpiochip_close(self.h)
    
    def cleanup(self):
        """Räume GPIO-Ressourcen auf (schließt gpiochip)."""
        lgpio.gpiochip_close(self.h)


    def brief_eingeworfen(self):
        """Meldet einen neuen Brief an die API mit aktuellem UTC-Timestamp."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        response = requests.post(f"{self.api}/new_letter", json={"serial_number": self.serial_number, "time": timestamp})
        print("Brief eingeworfen:", response.json())
        return response.json()

    def klappe_geoeffnet(self):
        """Interner Hook, wird aufgerufen wenn Klappe geöffnet wurde (Platzhalter)."""
        print("Klappe wurde geöffnet.")
        return

    def test_connection(self):
        """Prüft, ob die API erreichbar ist (Endpoint /status) und gibt True/False zurück."""
        response = requests.post(f"{self.api}/status", json={})
        print("API Status:", response.json())
        status = response.status_code
        if status != 200:
            print("Fehler bei der Verbindung zur API:", status)
            return False
        else:
            return True
# Globale Instanz
hw = BriefkastenHW()