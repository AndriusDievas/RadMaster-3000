from PyQt6 import QtWidgets, QtCore, QtGui
import sys

import RTout
import GMapp
import var
import time
import ports

config = var.config_folder

class ThreadManager(QtCore.QObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        self.GMThread = None
        self.RToutThread = None
        self.portThread = None
        self.statusThread = None
        self.progressBarThread = None

    # Thread Create
    def create_GM_Thread(self):
        self.GMThread = QtCore.QThread()
        self.GMWorker = GM_Worker()
        self.GMWorker.moveToThread(self.GMThread)
        self.GMThread.started.connect(self.GMWorker.startGM)
        self.GMWorker.finished.connect(self.GMThread.quit)
        self.GMWorker.finished.connect(self.GMWorker.deleteLater)
        self.GMThread.finished.connect(self.GMThread.deleteLater)
        self.GMThread.start()
        
    def create_RTout_Thread(self):
        self.RToutThread = QtCore.QThread()
        self.RToutWorker = RTout_Worker()
        self.RToutWorker.moveToThread(self.RToutThread)
        self.RToutThread.started.connect(self.RToutWorker.startRTout)
        self.RToutWorker.finished.connect(self.RToutThread.quit)
        self.RToutWorker.finished.connect(self.RToutWorker.deleteLater)
        self.RToutThread.finished.connect(self.RToutThread.deleteLater)
        self.RToutThread.start()
    
    def create_portSet_Thread(self):   
        self.portThread = QtCore.QThread()
        self.portWorker = portSet_Worker(self.parent.ui)
        self.portWorker.moveToThread(self.portThread)
        self.portThread.started.connect(self.portWorker.startPortSet)
        self.portWorker.finished.connect(self.portThread.quit)
        self.portWorker.finished.connect(self.portWorker.deleteLater)
        self.portThread.finished.connect(self.portThread.deleteLater)
        self.portThread.start()
           
    def create_progressBar_Thread(self):
        self.progressBarThread = QtCore.QThread()
        self.progressBarWorker = progressBar_Worker()
        self.progressBarWorker.started.connect(self.parent.progressBar.show)
        self.progressBarWorker.valueChanged.connect(self.parent.progressBar.setValue)
        self.progressBarWorker.finished.connect(self.parent.progressBar.hide)
        self.progressBarWorker.moveToThread(self.progressBarThread)
        self.progressBarThread.started.connect(self.progressBarWorker.startBar)
        self.progressBarWorker.finished.connect(self.progressBarThread.quit)
        self.progressBarWorker.finished.connect(self.progressBarWorker.deleteLater)
        self.progressBarThread.finished.connect(self.progressBarThread.deleteLater)
        self.progressBarWorker.finished.connect(self.parent.progressBar.show)
        # self.progressBarWorker.finished.connect(self.parent.progressBar.setValue)
        self.progressBarThread.start()
        
    def create_nono_Thread(self):   
        self.nonoThread = QtCore.QThread()
        self.nonoWorker = ForTheLoveOfGodPleaseDontUseThis()
        self.nonoWorker.moveToThread(self.nonoThread)
        self.nonoThread.started.connect(self.nonoWorker.ohnoyoudidnt)
        self.nonoWorker.finished.connect(self.nonoThread.quit)
        self.nonoWorker.finished.connect(self.nonoWorker.deleteLater)
        self.nonoThread.finished.connect(self.nonoThread.deleteLater)
        self.nonoThread.start()
        
    def create_print_Thread(self):
        self.printThread = PrintWorker(parent=self)
        self.printThread.newText.connect(self.parent.debug.append)
        sys.stdout = self.printThread
        self.printThread.start()
        
# ----------------------------- Thread stopping -------------------------------
        
    def stopGM(self):
        # if self.portSet_Thread is not None:
            self.GMWorker.stop()
            self.GMThread.quit()
            self.GMThread.wait()
            # self.GMThread = None
      
    def stopRTout(self):
        if self.RTout_Thread is not None:
            self.RToutWorker.stop()
            self.RToutThread.quit()
            self.RToutThread.wait()
            self.RToutThread = None
            
    def stopCPS(self):
        if self.create_CPS_Thread is not None:
            self.CPSWorker.stop()
            self.CPSThread.quit()
            self.CPSThread.wait()
            self.CPSThread = None        
            
    def stopPortSet(self):
        if self.portSet_Thread is not None:
            self.portWorker.stop()
            self.portThread.quit()
            self.portThread.wait()
            self.portThread = None
    
    def stopstartIndicators(self):
        if self.indicator_Thread is not None:
            self.statusWorker.stop()
            self.statusThread.quit()
            self.statusThread.wait()
            self.statusThread = None 
            
    
# ========================= Worker Classes ====================================
  
# ----------------------- Port set and indicator class ------------------------  
             
class portSet_Worker(QtCore.QObject):
        
    def __init__(self, ui):
        super().__init__()
        self._stop = False
        self.ui = ui
    
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    
    @QtCore.pyqtSlot()

    def startPortSet(self):
                   
        print('portSet_Worker class loaded (Threads.py)')
        
        self.started.emit()
        print('portSet_Worker.startPortSet() started (Threads.py)')
        
        for i in range(1,17):
            indicator_name = f"indicatorModule_{i}"
            indicator = getattr(self.ui, indicator_name)
            indicator.setPixmap(QtGui.QPixmap(":/LED/resources/indicator/off.png"))
        
        var.portsReady = 0 
        ports.portSet()
        
        while var.portsReady == 0:
            continue
    
        print('\nstartStatus() started (Threads.py)')
        print('var.LEDstart -', var.LEDstart, ' [1] (Threads.py)')
        
        with open(config/'ports.txt', 'r') as f:
            i = 1
            # Read each line from the file
            for line in f:
                # Check if the line contains the string "None"
                if "None" in line:
                    # If the line contains "None", do nothing and continue to the next line
                    indicator_name = f"indicatorModule_{i}"
                    indicator = getattr(self.ui, indicator_name)
                    indicator.setPixmap(QtGui.QPixmap(":/LED/resources/indicator/red.png"))
                    i += 1
                    continue
                else:
                    indicator_name = f"indicatorModule_{i}"
                    indicator = getattr(self.ui, indicator_name)
                    indicator.setPixmap(QtGui.QPixmap(":/LED/resources/indicator/green.png"))
                    i += 1
        
        print('startStatus() Completed (Threads.py)')
        self.finished.emit()
        
    def stop(self):
        self._stop = True   
        
# ----------------------- GM data read class ---------------------------------- 
       
class GM_Worker(QtCore.QObject):
    print('GM_Worker class loaded (Threads.py)')
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self._stop = False
        
    @QtCore.pyqtSlot()
    
    def startGM(self):
        self.started.emit()
        print("\nGM_Worker.startGM() started (Threads.py)")

        GMapp.Run()
        
        self.finished.emit()
                
    def stop(self):
        self._stop = True    

# --------------------- Real time out and CPS class ---------------------------

class RTout_Worker(QtCore.QObject):
       
    def __init__(self):
        super().__init__()
        self._stop = False
 
    print('RTout_Worker class loaded (Threads.py)')
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    
    @QtCore.pyqtSlot()

    def startRTout(self):
        self.started.emit()
        app = QtWidgets.QApplication.instance()
        main_window = app.activeWindow()
        import re
        
        print("\nRTout_Worker.startRTout() started (Threads.py)\n")
        
        while var.CPSout == 0:
            continue
        
        while var.CPSout == 1:

            time.sleep(1)
            
            for module in var.module_list:
 
                det1cps = var.CPS1[module]
                det2cps = var.CPS2[module]
                counts = round((var.det1[module] + var.det2[module]) / 2, 0)
                auSv = var.auSv[module]
                modulecps = (det1cps + det2cps) / 2
                det1uSv = round(det1cps * var.CF, 3) # CHANGE EQUATION!
                det2uSv = round(det2cps * var.CF, 3)
                moduleuSv = (det1uSv + det2uSv) / 2
    
                module_num = re.search(r'\d+', module).group()      
                
                setattr(RTout, f"m{module_num}RToutCPS", int(round(modulecps, 0)))
 
                setattr(RTout, f"m{module_num}RToutCPSdet1", round(det1cps, 0))
                setattr(RTout, f"m{module_num}RToutCPSdet2", round(det2cps, 0))
                
                setattr(RTout, f"m{module_num}RToutuSv", round(moduleuSv, 3))
                
                setattr(RTout, f"m{module_num}resultCounts", round(counts, 0))
                setattr(RTout, f"m{module_num}resultuSv", round(auSv, 3))
                
            for i in range(1, 16):
                
                CPS = getattr(main_window, f"CPS_m{i}")
                uSv = getattr(main_window, f"uSv_m{i}")
                CPSVar = getattr(RTout, f"m{i}RToutCPS")
                uSvVar = getattr(RTout, f"m{i}RToutuSv")
                
                if CPSVar >= var.CPSthreshold:
                    bg = QtGui.QPixmap(":/bg/resources/bg/cps_frame_high.png")
                elif CPSVar == 0 or CPSVar == 1:
                    bg = QtGui.QPixmap(":/bg/resources/bg/cps_frame.png")
                                
                label = getattr(main_window, f"cps_bg_m{i}")
                label.setPixmap(bg)
    
                CPS.setText(str(CPSVar))
                uSv.setText(str(uSvVar))
        
        print('Loop stopped')
        self.resetRTout()   
        self.finished.emit()
        
            # ------ Used for individual detectors if necessary ---------------
            # for i in range(17, 33):
            #     lcdCPSWidget = getattr(main_window, f"WIDGET_NAME_{i}") #RENAMED
            #     lcdCPSVar = getattr(RToutvar, f"m{i-16}RToutCPSdet1")
            #     lcdCPSWidget.display(lcdCPSVar)
            
            # for i in range(33, 49):
            #     lcdCPSWidget = getattr(main_window, f"WIDGET_NAME_{i}") #RENAMED
            #     lcdCPSVar = getattr(RToutvar, f"m{i-32}RToutCPSdet2")
            #     lcdCPSWidget.display(lcdCPSVar)
        
    def resetRTout(self):
        self.started.emit()
        app = QtWidgets.QApplication.instance()
        main_window = app.activeWindow()
        print("\nRTout_Worker.RToutreset() started (Threads.py)\n")
        time.sleep(1)
        bg = QtGui.QPixmap(":/bg/resources/bg/cps_frame.png")
        
        results = getattr(main_window, "results_frame")
        results.setVisible(True)
        
        time.sleep(0.5)
        
        for i in range(1, 16):
            print("Resetting RTout ", i)
            # CPS = getattr(main_window, f"CPS_m{i}")
            # uSv = getattr(main_window, f"uSv_m{i}")
            
            resultOut = getattr(main_window, f"counts_{i}")
            resultuSv = getattr(main_window, f"res_uSv_{i}")
            
            counts = int(getattr(RTout, f"m{i}resultCounts"))
            auSv = getattr(RTout, f"m{i}resultuSv")
            
            resultOut.setText(str(counts))
            resultuSv.setText(str(auSv))
            
            label = getattr(main_window, f"cps_bg_m{i}")
            label.setPixmap(bg)            
            
        print("\nRToutreset() stopped (Threads.py)")
   
        self.finished.emit()
        print("\nRTout_Worker.startRTout() stopped (Threads.py)")

    def stop(self):
        self._stop = True

        
# -------------------------- ProgressBar Class --------------------------------

class progressBar_Worker(QtCore.QObject):
    
    valueChanged = QtCore.pyqtSignal(int)
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self._stop = False

    @QtCore.pyqtSlot()
    def startBar(self):
        self.started.emit()
        self.valueChanged.emit(0)

        step_size = 100 / (var.T)

        while not var.startProgressBar == 1:
            continue

        start_time = time.time()

        for i in range(var.T):
            value = round((i + 1) * step_size)
            self.valueChanged.emit(value)  # Emit the updated value
            time.sleep(1)
                        
            if time.time() - start_time >= var.T:
                self.valueChanged.emit(100)  # Update the progress bar to 100%
                print('Time >', var.T, ' Setting progressBar to 100 (Threads.py)')
            if var.stop == 1: #value == 100 or 
                print('progressBar reached 100% or var.stop changed to 1. Stopping thread', 'progressBar value -', value, 'var.stop -', var.stop, ' (Threads.py)')
                var.startProgressBar = 0
                self.valueChanged.emit(0)
                self.finished.emit()
                return

        self.valueChanged.emit(0)
        self.finished.emit()
    
    def stop(self):
        self._stop = True  

# ----------------------- print() re-route to debug window --------------------

class PrintWorker(QtCore.QThread):
    newText = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.buffer = ''

    def run(self):
        while True:
            if self.buffer:
                self.newText.emit(self.buffer)
                self.buffer = ''
            time.sleep(0.1)

    def write(self, text):
        self.buffer += text

    def flush(self):
        self.newText.emit(self.buffer)
        self.buffer = ''

    def __del__(self):
        sys.stdout = sys.__stdout__
    
    def stop(self):
        self._stop = True  


# ------------------ This app can't run without this class --------------------
      
class ForTheLoveOfGodPleaseDontUseThis(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._stop = False
 
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    
    @QtCore.pyqtSlot()
    def ohnoyoudidnt(self):
        self.started.emit()
        app = QtWidgets.QApplication.instance()
        main_window = app.activeWindow()
        
        colors = ['background-color: red;', 'background-color: black;']
        while True:
            for color in colors:
                main_window.setStyleSheet(color)
                time.sleep(0.2)       