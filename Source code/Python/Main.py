import resources # Do not delete. GUI resource file

import sys
import os

import math
import re
import serial.tools.list_ports

from PyQt6 import QtWidgets
from Threads import ThreadManager 
from PyQt6 import QtGui
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtGui import QKeySequence, QShortcut

import var
from layout import Ui_MainWindow

def portClose():
    
    print('\nportClose() started. Closing all ports')
    with open(var.config_folder/"moduleID.txt") as f:
        target_ids = {line.split()[0]: line.split()[2] for line in f}
    
    # Find available COM ports
    ports = list(serial.tools.list_ports.comports())
    
    # Initialize dictionary to store ports that match target IDs
    matched_ports = {}
    
    # Loop through each port
    for port in ports:
        try:
            # Open port and read data
            ser = serial.Serial(port.device, 9600, timeout=1)
            data = ser.readline().decode("utf-8").strip()

            # Loop through target IDs and check if data matches
            for id_key, id_value in target_ids.items():
                match = re.search(fr"\b{id_value}\b", data)
                if match:
                    matched_ports[id_key] = port.device
                    ser.close()
                    break
        except Exception as error:
            print(error)
            continue
        
# ========================== Main Window ======================================

# thread = QThreadPool()  
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
                   
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.ui = self
                
        self.threadManager = ThreadManager(self)

        # Connect signals and buttons
        self.buttonStart.clicked.connect(self.Start)
        self.buttonStop.clicked.connect(self.Stop)    
        self.buttonPorts.clicked.connect(self.SetPorts)
        self.buttonWrite.clicked.connect(self.fileWrite)
        self.buttonReport.clicked.connect(self.openReport)
        
        self.boxSeconds.valueChanged.connect(self.spinAction)
        self.boxMinutes.valueChanged.connect(self.spinAction)
        self.boxCPS.valueChanged.connect(self.spinCPS)
        
        # Key shortcuts
        self.themeShortcut = QShortcut(QKeySequence("T"), self)
        self.importantShortcut = QShortcut(QKeySequence("end"), self)
        self.StartShortcut = QShortcut(QKeySequence("space"), self)
        self.debugShortcut = QShortcut(QKeySequence("d"), self)
        self.themeShortcut.activated.connect(self.toggle_theme)
        self.importantShortcut.activated.connect(self.nono)
        self.StartShortcut.activated.connect(self.Start)
        self.debugShortcut.activated.connect(self.showDebug)
        
        # Initial GUI conditions
        self.debugVisible = False
        self.debug_frame.setVisible(False)
        self.results_frame.setVisible(False)
        self.buttonDebug.clicked.connect(self.showDebug)
        self.buttonStart.setEnabled(True)

        # Startup threads
        self.threadManager.create_portSet_Thread()
        self.threadManager.create_print_Thread()

        # Flag to keep track of which theme is currently used
        self.use_dark_theme = False  
        
# ======================= Button functionality ================================  
                  
    def toggle_theme(self):       
        styleDark = "color: white;"
        styleLight = "color: black;"
        
        self.use_dark_theme = not self.use_dark_theme
        theme = styleDark if self.use_dark_theme else styleLight
        
        # Module status theme
        self.status_label.setStyleSheet(theme)
        module_numbers = [getattr(self, f"module_number_{i}") for i in range(1, 17)]
        for module_number in module_numbers:
            module_number.setStyleSheet(theme)
        
        labels = ['Appname', 'count_time_label','time_label','time_unit_label','labelMin','labelSec','labelCPS']
        
        for label_name in labels:
            label = getattr(self, label_name)
            label.setStyleSheet(theme)
        
        # background color
        pal = self.palette()
        if self.use_dark_theme:
            pal.setColor(QPalette.ColorRole.Window, QColor('#101010')) # black
        else:
            pal.setColor(QPalette.ColorRole.Window, QColor('#f0f0f0')) # gray
        self.setPalette(pal)
        
        # Output frame background
        if self.use_dark_theme:
            self.CPS_bg.setPixmap(QtGui.QPixmap(":/bg/resources/bg/cps_bg_dark.png"))
        else:
            self.CPS_bg.setPixmap(QtGui.QPixmap(":/bg/resources/bg/cps_bg.png"))  
        
    def Start(self):  
        self.results_frame.setVisible(False)  
        self.threadManager.create_GM_Thread()  
        self.threadManager.create_RTout_Thread() 
        self.threadManager.create_progressBar_Thread()

        var.stop = 0
        var.portsReady = 0
        var.LEDstart = 1
        var.startProgressBar = 0
        var.CPSout = 1

    def Stop(self):     
        var.stop = 1
        var.CPSout = 0
        var.portsReady = 0
        var.LEDstart = 0
        var.startProgressBar = 0
                        
        portClose()
        
    def SetPorts(self):
        var.portsReady = 0
        self.threadManager.create_portSet_Thread()

    def fileWrite(self):
        from GMapp import write
        write()
        
    def spinAction(self):  
        self.Console.clear()
        value = self.boxSeconds.value()
        value2 = self.boxMinutes.value()
               
        var.T = value + value2*60
        if var.T == 0:
            self.Console.append("Cannot set to " + str(var.T) + ", defaulting to 1")
            self.time_label.setText("0")
            var.T = 1
        if var.T < 60:
            self.Console.append("Count time set to " + str(var.T) + " seconds")
        if var.T == 60 or var.T > 60:
            self.Console.append("Count time set to " + str(math.trunc(var.T/60)) + " minutes " 
                                      + str(round((var.T/60 - math.trunc(var.T/60))*60)) + " seconds")
        self.time_label.setText(str(var.T))
        
    def spinCPS(self):    
        self.Console.clear()
        CPS = self.boxCPS.value()
        
        var.CPSthreshold = CPS
        self.Console.append('Bq threshold set to ' + str(CPS))
        
        
    def openReport(self):
        os.system(r'start ' + var.report_path)
        
    def openData(self):
        os.system(r'start ' + var.data_path)     
        
    def showDebug(self):        
        self.debugVisible = not self.debugVisible
        self.debug_frame.setVisible(self.debugVisible)
        
    def nono(self):
        self.threadManager.create_nono_Thread()

# ========================== App execute ======================================

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()

# =================== Is run after window close ===============================

var.stop = 1
var.LEDstart = 0
var.GMdone = 0
var.portsReady = 0
var.exit = 1

print('\n--- Window closed, setting variables for script termination ---')
print('Var.stop set to - ', var.stop, '(Main.py)')
print('Var.LEDstart set to - ', var.LEDstart,'(Main.py), do I need this?')
print('Var.GMdone set to - ', var.GMdone,'(Main.py)')
print('Var.portsReady set to - ', var.portsReady,'(Main.py)')
print('Var.exit set to - ', var.exit,'(Main.py)')





portClose()

print('\nApp closed')
