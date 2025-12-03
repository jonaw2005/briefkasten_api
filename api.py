from flask import Flask, request, jsonify
from uuid import uuid4
from datetime import datetime, timezone
import time
import re
import threading

import database_handler

# /c:/Coding/briefkasten/api.py

app = Flask(__name__)
_start_time = time.time()
_users = {}


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

entriegeln_flag = False
entriegeln_lock = threading.Lock()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

# @param route: "/status" method: POST returns if a new letter is present with a given serial number
@app.route("/status", methods=["POST", "GET"])
def status():
    if not request.is_json:
        #return jsonify({"error": "expected JSON"}), 400
        pass
    uptime = time.time() - _start_time
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "time": now_iso(),
        "uptime_seconds": round(uptime, 3)
    })


@app.route("/letters", methods=["POST"])
def letters():
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 400
    data = request.get_json()
    mac_address = data.get("mac_address")
    if not isinstance(mac_address, str) or not mac_address:
        return jsonify({"error": "field 'mac_address' is required and must be a non-empty string"}), 400
    #if not isinstance(mac_address, str) or not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac_address):
    #    return jsonify({"error": "field 'mac_address' is required and must be a valid MAC address"}), 400

    db = database_handler.DatabaseHandler()

    # get the Serial Number by MAC address
    serial_number = db.getSerialNumberByMAC(mac_address)

    letters = db.getLetters(serial_number)

    return jsonify({"letters": letters}), 200


@app.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 400
    data = request.get_json()
    serial_number = data.get("serial_number")
    mac_address = data.get("mac_address")

    if not isinstance(mac_address, str) or not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac_address):
        return jsonify({"error": "field 'mac_address' is required and must be a valid MAC address"}), 400
    
    if not isinstance(serial_number, str) or not serial_number:
        return jsonify({"error": "field 'serial_number' is required and must be a non-empty string"}), 400

    db = database_handler.DatabaseHandler()
    #db.create_user_table()
    db.addUser(mac_address, serial_number)

    db.create_letter_table(serial_number)



    return jsonify("test"), 201

@app.route("/new_letter", methods=["POST"])
def new_letter():
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 400
    data = request.get_json()
    serial_number = data.get("serial_number")
    time = data.get("time")

    if not isinstance(serial_number, str) or not serial_number:
        return jsonify({"error": "field 'serial_number' is required and must be a non-empty string"}), 400

    db = database_handler.DatabaseHandler()

    db.addLetter(serial_number, time)

    return jsonify({"status": "letter added"}), 201


# MAC nicht Serial Number !!!!
@app.route("/entriegeln", methods=["POST"])
def entriegeln():
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 400
    data = request.get_json()
    serial_number = data.get("serial_number")
    if not isinstance(serial_number, str) or not serial_number:
        return jsonify({"error": "field 'serial_number' is required and must be a non-empty string"}), 400
    
    global entriegeln_flag
    with entriegeln_lock:
        entriegeln_flag = True
    return jsonify({"status": "entriegeln set to true"}), 200


@app.route("/frage_entriegeln", methods=["POST"])
def frage_entriegeln():
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 400
    data = request.get_json()
    serial_number = data.get("serial_number")
    if not isinstance(serial_number, str) or not serial_number:
        return jsonify({"error": "field 'serial_number' is required and must be a non-empty string"}), 400
    
    global entriegeln_flag
    with entriegeln_lock:
        entriegeln = entriegeln_flag
        if entriegeln_flag:
            entriegeln_flag = False
            return jsonify({"entriegeln": True}), 200
        else:
            return jsonify({"entriegeln": False}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)