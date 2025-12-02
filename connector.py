import requests
import datetime
from hw_code import hw
import time

serial_number = "SN123456"
api = "http://localhost:5000"



def entriegeln_loop():

    open = False

    while True:
        if not open:
            if entriegeln():
                print("entriegeln received")
                hw.servo_open()
                time.sleep(5)
                #hw.servo_close()
        time.sleep(5)


def entriegeln():
    response = requests.post(f"{api}/frage_entriegeln", json={"serial_number": serial_number})
    return response.json().get("entriegeln", False)



def brief_eingeworfen():
    time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    response = requests.post(f"{api}/new_letter", json={"serial_number": serial_number, "time": time})
    return response.json()


def klappe_geoeffnet():
    pass


