import requests
import json

mac = "00:1A:2B:3C:4D:5E"
serial = "SN987654"
time = "2024-06-01T12:00:00Z"

#print(requests.post("http://192.168.3.12:5000/entriegeln", json={
#    "serial_number": serial}).json())

#requests.post("http://192.168.3.12:5000/register", json={
#    "mac_address": mac, "serial_number": serial})

#print(requests.post("http://192.168.3.12:5000/letters", json={
#    "mac_address": mac}).json().get("letters"))

#print(requests.post("http://192.168.3.12:5000/new_letter", json={
#    "serial_number": serial, "time": time}).json())

#print(requests.post("http://192.168.3.12:5000/letters", json={
#    "mac_address": mac}).json())


def get_letters():
    response = requests.post("http://192.168.5.1:5000/letters", json={
        "mac_address": mac})
    data = response.json()
    letters = data.get("letters", [])
    # if API returned a JSON-encoded string, parse it
    if isinstance(letters, str):
        try:
            letters = json.loads(letters)
        except ValueError:
            letters = [letters]
    # normalize to a list
    if isinstance(letters, dict):
        letters = [letters]
    return list(letters)

print(len(get_letters()))