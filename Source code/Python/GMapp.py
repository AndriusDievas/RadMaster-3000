import serial
import time

import var
from datetime import datetime, timedelta
from PyQt6 import QtWidgets
# Create a dictionaries and lists to store the serial connections and other data
module_list = []

connections = {}

det1 = {}
det2 = {}
counts = {}
CPS1 = {}
CPS2 = {}
uSv1 = {}
uSv2 = {}
aCPS = {}
auSv = {}

det1_CPSlist = [] 
det2_CPSlist = [] 
det1_uSvlist = []
det2_uSvlist = []

config = var.config_folder
data = var.data_folder

def Run():

    app = QtWidgets.QApplication.instance()
    main_window = app.activeWindow()
    start = getattr(main_window, "buttonStart")
    stop = getattr(main_window, "buttonStop")
    saveData = getattr(main_window, "buttonWrite")
    openData = getattr(main_window, "buttonReport")
    ports = getattr(main_window, "buttonPorts")
    
    start.setEnabled(False)
    stop.setEnabled(True)
    openData.setEnabled(False)
    saveData.setEnabled(False)
    ports.setEnabled(False)
    
    print('\nGMapp.Run() started (GMapp.py)\n') 
    T = var.T
    start_time = time.time()
    # last_time = 0

    # Read the port configuration from the ports.txt file
    with open(config/'ports.txt', 'r') as f:
        port_config = f.readlines()
        
    print('\nPort initialization started (GMapp.py)')
    # Initialize the connections and event counters
    for line in port_config:
        module, port = line.strip().split(" = ")
        if port == "None":
            continue
            
        else:
            ser = serial.Serial(port.strip(), 115200, timeout=0.5)
            ser.set_buffer_size(rx_size=16384)
            
            connections[module] = ser
            module_list.append(module)
            det1[module] = 0
            det2[module] = 0
            CPS1[module] = 0
            CPS2[module] = 0
            aCPS[module] = 0
            auSv[module] = 0
            
            var.connections[module] = ser
            var.module_list.append(module)
            var.det1[module] = 0
            var.det2[module] = 0
            var.CPS1[module] = 0
            var.CPS2[module] = 0
            var.aCPS[module] = 0
            var.auSv[module] = 0
                        
    print('\nPort initialization complete (in GMapp.py)')
          
    # ============== Read the serial data from all connected modules ==============
    
    print('\nSerial read and data accumulation started (in GMapp.py)')
    
    var.startProgressBar = 1
    # var.CPSthreadStart = 1
    
    print('var.progressBar set to ', var.startProgressBar, 'ProgressBar started')
    # print('var.CPSThreadStart set to ', var.CPSthreadStart)
    
    
   

    while True:   
        if var.stop == 1:
            print('Script sopped (var.stop set to -', var.stop, ') - breaking out of read loop (in GMapp.py)')
            break
    
        elapsed_time = time.time() - start_time
        
        var.elapsedTime = elapsed_time # needed for thread
        
        for module, ser in connections.items():
            if ser:
                line = ser.readline().decode().rstrip()
                                
                if "Mod-" in line:
                    counts = line.split()
                    
                    det1[module] += int(counts[1])
                    det2[module] += int(counts[2])

                    var.CPS1[module] = int(counts[1])
                    var.CPS2[module] = int(counts[1])
                    
# =============================== Output calculations =========================
    
        if elapsed_time >= T or var.stop == 1:
            print('\n Time > ', var.T, ' - starting output calculations (in GMapp.py)\n')
            print('Final calculations:\n')
            
            # Read the coefficients from the file
            with open(config/'coef.txt', 'r') as f:
                lines = f.readlines()
                
                coef = {}
                for i in range(1, len(lines), 3):
                    module = f"Module-{i//3+1}"
                    if lines[i].startswith('Detector'):
                        coef1 = float(lines[i].split('=')[1].strip())
                    else:
                        coef1 = 1.0
                    if lines[i+1].startswith('Detector'):
                        coef2 = float(lines[i+1].split('=')[1].strip())
                    else:
                        coef2 = 1.0
                    coef[module] = (coef1, coef2)
                    print(f"{module} Coefficients: {coef1}, {coef2}")
                    print(connections)
                    
            # Print the event counts and break out of the loop
            for module, ser in connections.items():
                if ser:
                    # Get the coefficients for this module
                    coef1, coef2 = coef.get(module, (1.0, 1.0))
                    print('COEF1 = ', coef1)
                    print('COEF2 = ', coef2)
                    CPS1[module] = round((det1[module] * coef1) / T, 2) 
                    CPS2[module] = round((det2[module] * coef2) /T, 2)
                    aCPS[module] = round((CPS1[module] + CPS2[module]) / 2, 2)
                    
                    # uSv/h = (Counts * 19.5) / (t * 0.0081) Formula for SBT-10
                    # conversion factor for the SBT-10 GM tube is typically around 0.0081 uSv/h per CPS
                    
                    uSv1[module] = round((CPS1[module])*var.CF, 5)
                    uSv2[module] = round((CPS2[module])*var.CF, 5)
                    auSv[module] = round((uSv1[module] + uSv2[module]) / 2, 5)
                    
                    var.det1[module] = det1[module] * coef1
                    var.det2[module] = det2[module] * coef2
                    var.auSv[module] = auSv[module]
                    
                    print("=", module, "=")
                    print("Total counts: Det1 [", det1[module] * coef1, "] | Det2 - [", det2[module] * coef2, "]")
                    print("CPS: Det1 [", CPS1[module], "] | Det2 - [", CPS2[module], "]")
                    print("uSv: Det1 [", uSv1[module], "] | Det2 - [", uSv2[module], "]")
                    print("CPS - [", aCPS[module], "]")
                    print("uSv - [", auSv[module], "]")
                    print("\n")
                    
                    ser.close()
            var.stop = 1
            var.CPSthreadStart = 0
            print('Time > ', var.T, 'and output calculations complete - exiting read/output loop (in GMapp.py)\n')
            print('var.stop set to - ', var.stop, ' (in GMapp.py)')
            break
            
# ============================== Script end ===================================

    var.stop = 1  
    var.CPSout = 0
    # var.CPSthreadStart = 0
    # print('set CPSthreadStart to', var.CPSthreadStart, ' (in GMapp.py)')
    print('\nSet var.stop to ', var.stop, '(again. just in case. This code is a bowl of spaghetti), (in GMapp.py)')    
    
    start.setEnabled(True)
    stop.setEnabled(False)
    openData.setEnabled(True)
    saveData.setEnabled(True)
    ports.setEnabled(True)
    
                
# ============================ Write to file ==================================

def write():
        
    current_time = datetime.now()
    end_time = current_time + timedelta(seconds = var.T)
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    file_report = open(data/ 'GM-report.txt', 'w')
    file_report.write('G.M. Module counting results:')
    
    for module, ser in connections.items():
        if ser:
            Module_str = str(module)
            Detector1_str = str('Detector 1: ' + str(det1[module]) + ' counts')
            Detector2_str = str('Detector 2: ' + str(det2[module]) + ' counts')
             
            file_report.write('\n\n' + Module_str + '\n')
            file_report.write(Detector1_str + '\n' + Detector2_str)
                           
    if var.T < 60:
        count_time = f"{var.T} seconds"
    else:
        count_time = f"{var.T//60} minutes"
        if var.T % 60 != 0:
            count_time += f" and {var.T%60} seconds"
    
    file_report.write(f"\n\nCount time: {count_time}")
    file_report.write(f"\n\nPerformed on: {end_time_str}")
               
    file_report.close()

    print('Results saved to /' + str(data) + ' folder (in GMapp.py)')
