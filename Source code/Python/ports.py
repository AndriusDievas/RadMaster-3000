import serial.tools.list_ports
import re
import var
import os
from PyQt6 import QtWidgets
import time

config = var.config_folder

def portSet():
    time.sleep(2)
    app = QtWidgets.QApplication.instance()
    main_window = app.activeWindow()
    start = getattr(main_window, "buttonStart")
    stop = getattr(main_window, "buttonStop")
    saveData = getattr(main_window, "buttonWrite")
    openData = getattr(main_window, "buttonReport")
    portsButton = getattr(main_window, "buttonPorts")
    
    start.setEnabled(False)
    stop.setEnabled(False)
    openData.setEnabled(False)
    saveData.setEnabled(False)
    portsButton.setEnabled(False)
    
    var.portsReady = 0
    # Read target IDs from text file
    with open(config/"moduleID.txt") as f:
        target_ids = {line.split()[0]: line.split()[2] for line in f}

    # Find available COM ports
    ports = list(serial.tools.list_ports.comports())

    # Initialize dictionary to store ports that match target IDs
    matched_ports = {}

    # Loop through each port
    for port in ports:
        try:
            # Open port and read data
            ser = serial.Serial(port.device, 9600, timeout=2, )#buffersize=8192
            data = ser.readline().decode("utf-8").strip()
            ser.close()

            # Loop through target IDs and check if data matches
            for id_key, id_value in target_ids.items():
                match = re.search(fr"\b{id_value}\b", data)
                if match:
                    matched_ports[id_key] = port.device
                    break

        except Exception as error:
            print(error)
            continue

    # =========================================================================
    print('')
    
    if not os.path.isfile(config/"ports.txt"):
        with open(config/"ports.txt", "w") as f:
            for i in range(1,17):
                f.write(f"Module-{i}" + ' = None')
            print("Created moduleID.txt file with default values (in ports.py)")
               
    with open(config/'ports.txt', 'w') as f:
        i = 1
        for id_key, id_value in target_ids.items():
            if id_key in matched_ports:
                print(f"Module-{i} found on {matched_ports[id_key]}")
                var_name = f"Module-{i}"
                locals()[var_name] = matched_ports[id_key]
                f.write(f"{var_name} = {matched_ports[id_key]}\n")
                i = i + 1
            else:
                print(f"Module-{i} not found")
                var_name = f"Module-{i}"
                locals()[var_name] = None
                f.write(f"{var_name} = None\n")  # Append to file
                i = i + 1
    print('')   
    var.portsReady = 1
    
    start.setEnabled(True)
    openData.setEnabled(True)
    saveData.setEnabled(True)
    portsButton.setEnabled(True)
    
    print('var.portsReady = 1 (in ports.py)\n')  
        
# portSet()
  
    

