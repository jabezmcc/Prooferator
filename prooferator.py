# Prooferator - Arduino-controlled "proofing" box for bread dough
# (c) 2022 - Jabez McClelland jabezmcc@gmail.com
# 
# Revision history
#
# 1/22/20222 - 0.1.1: trapped possible bad inputs.  Added temp units to temp. display and y-axis
#
# 1/15/2022 - 0.1.0: First version
#
import sys
import os
import xlsxwriter
import datetime as dt
import time
import numpy as np
import serial
import pathlib
import re
import platform
import subprocess

from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.uic import loadUiType

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import bread_img_rc

Ui_MainWindow, QMainWindow = loadUiType('prooferator.ui') 
Ui_AboutWindow, QAboutWindow = loadUiType('aboutProoferator.ui')

vers = '0.1.1'

class About(QAboutWindow, Ui_AboutWindow):
    def __init__(self):
        super(About,self).__init__()
        self.setupUi(self)
        self.versionLabel.setText("Version "+vers)
        self.licenseButt.clicked.connect(self.show_license)
        self.OKButt.clicked.connect(self.closeout)
        self.show()
        
    def show_license(self):
        p = platform.system()
        try:
            if p == 'Linux':
                subprocess.run(['xdg-open', 'LICENSE.txt'],check=True)
            elif p=='Windows':
                os.system('start LICENSE.txt')
            else:
                os.system('open LICENSE.txt')
        except:
             QMessageBox.warning(self,'Error','Unable to open license document')
                
    def closeout(self):
        self.close()

class Main(QMainWindow, Ui_MainWindow):
    plotexists = False
    takedata = True
    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)
        self.actionExitButton.triggered.connect(self.exit)
        self.actionAbout.triggered.connect(self.openabout)
        self.startButton.clicked.connect(self.start_data)
        self.stopButton.clicked.connect(self.stop_data)
        self.updateButton.clicked.connect(self.update_setpoint)
        self.FradioButton.setText('\xB0F')
        self.CradioButton.setText('\xB0C')
        cwd = str(pathlib.Path(__file__).parent.resolve())
        self.data_dest = cwd +'/proofingbox.xlsx'
        self.dataSaveLabel.setText('Data will be saved in '+self.data_dest)
        self.changeDataButton.clicked.connect(self.change_data_dest)
        self.timeintervalBox.setText('0.1')
        self.setpointC = self.get_arduino_setpoint()
        self.setpoint = self.setpointC   
        if self.FradioButton.isChecked():
            self.currentTempLabel.setText('--.-\xB0F')
            self.setpointF = self.setpointC*9./5. + 32.
            self.setpointBox.setText('{:3.1f}'.format(self.setpointF))
            self.setpoint = self.setpointF
        else:
            self.currentTempLabel.setText('--.-\xB0C')
            self.setpointBox.setText('{:4.2f}'.format(self.setpointC))
        self.canvas = FigureCanvas(plt.Figure(figsize=(15, 6)))
        self.mainplot_layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.ax.set_xlabel("Time")
        if self.FradioButton.isChecked():
            self.ax.set_ylabel("Temperature, \xB0F")
        else:
            self.ax.set_ylabel("Temperature, \xB0C")       
        self.ax.set_title("Proofing Box Temperature Log")
        self.ax.set_position([.15,.15,.75,.75])
        self.ax.tick_params(axis='both',direction='in')
        self.ax.set_ylim(self.setpoint*0.75,self.setpoint*1.25)
        self.ax.set_xlim(dt.datetime.now(),dt.datetime.now()+dt.timedelta(hours=2))

    def openabout(self):
        self.aboutwin = About()

    def get_arduino_setpoint(self):
        filename = './arduino_folder/proofingbox/proofingbox.ino'
        fin = open(filename,'r')
        lines = fin.readlines()
        fin.close()
        for line in lines:
            s = re.search('setPoint = (\d\d.\d\d)',line)
            if s:
                return float(s.group(1))

    def get_temp(self):
        try:
            ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
            rawdata = ser.readline()
            ser.close()
            temperature = float(rawdata.decode('UTF-8').strip('\n'))
        except:
            print('Error reading temperature, using old temperature')
            temperature = float(self.currentTempLabel.text())
        if self.FradioButton.isChecked():
            temperature = temperature*9./5. + 32.
        return temperature
    
    def get_temp_dummy(self):
        temperature = self.setpointC + 5.*(np.random.rand()-0.5)
        if self.FradioButton.isChecked():
            temperature = temperature*9./5. + 32.
        return temperature 

    def start_data(self):
        try:
            ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
            dummy = False
        except:
            QMessageBox.warning(self,'Prooferator','No Arduino detected, simulating data')
            dummy = True
        self.takedata = True        
        self.wb = xlsxwriter.Workbook(self.data_dest)
        wbtimefmt = self.wb.add_format({'num_format': 'mmm d yyyy hh:mm:ss'})
        ws = self.wb.add_worksheet()
        ws.set_column(0,0,20)
        ws.set_column(1,1,15)
        ws.write(0,0,'Time')
        ws.write(0,1,'Temperature')
        times = []
        temps = []
        count = 0
        self.ax.cla()
        self.ax.set_xlabel("Time")
        if self.FradioButton.isChecked():
            self.ax.set_ylabel("Temperature, \xB0F")
        else:
            self.ax.set_ylabel("Temperature, \xB0C")  
        self.ax.set_title("Proofing Box Temperature Log")
        while self.takedata:
            count += 1
            try:
                plt.pause(60*float(self.timeintervalBox.text()))
            except:
                QMessageBox.warning(self,'Prooferator error','Invalid entry for time interval')
                break 
            print('plotting point',count)
            times.append(dt.datetime.now())
            ws.write(count,0,times[-1],wbtimefmt)
            if dummy:
                current_temp = self.get_temp_dummy()
            else:
                current_temp = self.get_temp()
            print(current_temp)
            unittext = '\xB0C'
            if self.FradioButton.isChecked():
                 unittext = '\xB0F'
            self.currentTempLabel.setText("{:3.1f}".format(current_temp)+unittext)
            temps.append(current_temp)
            ws.write(count,1,temps[-1])
            if self.plotexists:
                self.lin.remove()
            self.plot_data(data=[times,temps])

    def plot_data(self,data=[[0],[0]]):
        self.lin, = self.ax.plot(data[0],data[1],color='blue')
        self.canvas.draw()
        self.canvas.flush_events()
        self.plotexists = True       
    
    def stop_data(self):
        self.takedata = False
        qbox = QMessageBox.question(self,'Prooferator','Do you want to save data?',QMessageBox.Yes,QMessageBox.No)
        if self.plotexists:
            if qbox == QMessageBox.Yes:
                self.wb.close()
                QMessageBox.information(self,'Prooferator','Acquisition finished.\nData saved in'+self.data_dest)
        else:
            QMessageBox.information(self,'Prooferator','Please record some data first.')    

    def update_setpoint(self):
        try:
            self.setpoint = float(self.setpointBox.text())
        except:
            QMessageBox.warning(self,'Prooferator error','Invalid entry for setpoint')
            return
        self.setpointC = self.setpoint
        if self.FradioButton.isChecked():
            self.setpointC = (self.setpoint - 32.)*5./9.
        self.update_arduino(self.setpointC)

    def change_data_dest(self):
        fileName, _ = QFileDialog.getSaveFileName(self,"Select data destination file","./","Excel files (*.xlsx)")
        if fileName:
            strfN = str(fileName)
            if strfN[-5:] != '.xlsx':
                strfN = strfN + '.xlsx'
            self.data_dest = strfN
            self.dataSaveLabel.setText('Data will be saved in ' + strfN) 
    
    def update_arduino(self,setpoint):
        setpointtext = "{:4.2f}".format(setpoint)
        filename = './arduino_folder/proofingbox/proofingbox.ino'
        os.system('cp '+filename+' '+filename+'.bak')
        fin = open(filename,'r')
        lines = fin.readlines()
        fin.close()
        newlines = []
        p = re.compile('setPoint = \d\d\.\d\d')
        for line in lines:
            newlines.append(p.sub('setPoint = '+setpointtext,line))
        fout = open(filename,'w')
        fout.writelines(newlines)
        fout.close()
        u = os.system('arduino --upload '+filename)
        if u:
            QMessageBox.warning(self,'Prooferator','Unable to program Arduino.\nCheck connections.')
            os.system('cp '+filename+'.bak '+filename)
        else: 
            QMessageBox.information(self,'Prooferator','Arduino successfully updated.')

    def exit(self):
        qbox = QMessageBox.question(self,'Prooferator','Do you want to save data?',QMessageBox.Yes,QMessageBox.No)
        if qbox==QMessageBox.Yes:
            self.takedata=False
            try: 
                self.wb.close()
            except:
                pass
            sys.exit()
        else:
            self.takedata=False
            sys.exit()

    def closeEvent(self,event):
        qbox = QMessageBox.question(self,'Prooferator','Do you want to save data?',QMessageBox.Yes,QMessageBox.No)
        if qbox==QMessageBox.Yes:
            self.takedata=False
            try:
                self.wb.close()
            except:
                pass
            event.accept()
        else:
            self.takedata=False
            event.accept()

if __name__=="__main__":
    app = QApplication(sys.argv)
    main = Main()
    qtRectangle = main.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main.move(qtRectangle.topLeft())
    main.show()
    sys.exit(app.exec())
