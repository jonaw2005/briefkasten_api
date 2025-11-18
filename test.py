import requests

mac = "00:1A:2B:3C:4D:5E"
serial = "SN987654"
time = "2024-06-01T12:00:00Z"
#requests.post("http://localhost:5000/register", json={
#    "mac_address": mac, "serial_number": serial})

#print(requests.post("http://localhost:5000/letters", json={
#    "mac_address": mac}).json())

#print(requests.post("http://localhost:5000/new_letter", json={
#    "serial_number": serial, "time": time}).json())

print(requests.post("http://localhost:5000/letters", json={
    "mac_address": mac}).json())