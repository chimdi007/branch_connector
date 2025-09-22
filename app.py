from flask import Flask, jsonify, render_template, request
import json
import subprocess
import threading
import schedule
import time
from datetime import datetime
import requests
import logging
import os
import sys
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = os.urandom(24)


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """ Get absolute path to resource, works in dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores files here
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

file_path = resource_path("config.txt")

"""
Device is blank at first
Upon opening connector device, if device is not connected to any organisation, a setup template is returned, else the organisation 
"""
@app.route('/')
def index():
    global file_path
    config = {}

    try:
        # Try reading the existing config
        with open(file_path, 'r') as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file is missing or invalid JSON, treat as no setup
        print(f"Decode error: ")
        config = {}
    print("COnfig: ", config)
    # If the device is already linked to an organisation (dispensaryID present)
    if config.get('dispensaryID', ''):
        # Do not expose deviceID to the UI
        #config.pop('deviceID', None)
        return render_template('index.html', config=config)
    else:
        # Otherwise show setup screen
        return render_template('setup.html')





#Perfected!!!
@app.route('/device_activation', methods=['POST'])
def device_activation():
    global file_path
    #url = "http://127.0.0.1:5002/devices/branch_connector_activation"
    url = "https://api.prescribe.ng/devices/branch_connector_activation"
    try:
        data = request.form.to_dict()
        print("Data recieved: ", data)
        required_fields = ['username', 'password', 'dispensaryID', 'branchID']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return f'Missing fields: {", ".join(missing_fields)}', 400
        
        response = requests.post(url, json=data)
        if response.status_code == 200: #If server accepts device, set the configurations returned to config.txt
            response_json = response.json()
            config = response_json.get("config", response_json)
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)
            
            return render_template('index.html', config=config)
        
        else:
            return f'Branch connector activation failed: {response.text}', response.status_code

    except Exception as e:
        return f'Error activating connector: {str(e)}', 500





# Function to perform IP check at intervals, catch changes in public ipv4 and reconnect branch to PrescribeNG spine
#This service is only for small centers who can not afford a static ip address
def get_public_ip():
    global file_path
    url = "https://api.prescribe.ng/devices/update_ip"
    #url = "http://127.0.0.1:5002/devices/update_ip"
    
    #print("Checking ip...")
    
    # Read existing device configuration
    with open(file_path, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            return  #terminate if unable to decode configurations
        
    if not config:
        return #terminate if no configurations exists yet
    
    old_ip = config.get('oldIP', '')
    
    try:
        result = subprocess.run(['curl', '-4', 'ifconfig.me'], capture_output=True, text=True)
        if result.returncode == 0:
            new_ip = result.stdout.strip()
            if new_ip == old_ip:
                return #Just discontinue process if new IP is equal to old IP
        
        #If ipv4 change is detected, Update config and make an api call to prescribespine to reconnect branch. 
        #print("New IP: ", new_ip)  
        config['newIP'] = new_ip
        
        response = requests.post(url, json=config)
        
        #Only update config.txt if response is positive
        if response.status_code == 200:
            config['oldIP'] = new_ip
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)
        
        #Clear device and set it to dafault state if status code is 401
        elif response.status_code in [401, 403]:
            with open(file_path, 'w') as file:
                json.dump({}, file, indent=4)
                
    except Exception as e:
        print(f"Error retrieving public IPv4: {e}")
    return new_ip


#get_public_ip()
    
    

# Function to perform IP check
schedule.every(10).seconds.do(get_public_ip)

def start_scheduler():
    print("Scheduling started!")
    while True:
        schedule.run_pending()
        time.sleep(10)








#___________THIS PART OF THE CODE IS NOT IN USE________________
def start_scheduling():
    print("Scheduling2 started")
    global scheduling_running
    if not scheduling_running:
        scheduling_running = True
        while scheduling_running:
            schedule.run_pending()
            time.sleep(30)
        return jsonify({"message":"Scheduling started successfully."}), 200
    else:
        print("Scheduling is already running.")
        return jsonify({"message":"Scheduling is already running."}), 200



if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True  # Allows the program to exit if only daemon threads are left
    scheduler_thread.start()
    app.run(debug=False, host='0.0.0.0', port=4050, use_reloader=False)
