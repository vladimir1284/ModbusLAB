# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import qrc_resources
import sys
import serial

#add logging capability
import logging

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu

class RTUMonitor(QtCore.QThread):
    coilsRead = QtCore.pyqtSignal(tuple, tuple)
    
    def __init__(self, ConfigurationData, SPC, stationNumber, parent=None):
        self.reconfigure(ConfigurationData,SPC,stationNumber)
        super(RTUMonitor, self).__init__(parent)
#        self.logger = modbus_tk.utils.create_logger("console")
        self.master.set_timeout(5.0)
        self.master.set_verbose(True)
#       self.logger.info("connected")
        
        # Candado
        self.mutex = QtCore.QMutex()
        
    def reconfigure(self, ConfigurationData, SPC, stationNumber):
            self.port = str(SPC[0])
            self.baudrate = int(SPC[1])
            self.bytesize = int(SPC[2])
            self.parity = str(SPC[3])
            self.stopbits = int(SPC[4])
            self.xonxoff = int(SPC[5])
            self.stationNumber = stationNumber
            self.ConfigurationData = ConfigurationData
            self.master = modbus_rtu.RtuMaster(serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits, xonxoff=self.xonxoff))
        
        
    def run(self):
        while True:
            self.mutex.lock()
            try:
                inputs = self.master.execute(2, cst.READ_COILS, self.ConfigurationData[2], self.ConfigurationData[0])
                outputs = self.master.execute(2, cst.READ_COILS, self.ConfigurationData[3], self.ConfigurationData[1])
                self.coilsRead.emit(inputs, outputs)
            except:
                pass
            self.mutex.unlock()
            self.msleep(1000) #ms
            
    def sendMessage(self, Message):
        self.mutex.lock()
        try:
            if (Message[1] == 5) | (Message[1] == 6):
                response =  self.master.execute(Message[0],Message[1],Message[2],output_value=Message[3])
            else:
                response =  self.master.execute(Message[0],Message[1],Message[2],Message[3])
        except:
            pass
        self.mutex.unlock()
        
class PLCdigitalIO(QtGui.QGroupBox):    
    def __init__(self, parent, Nin, Nout, BaseAddIn, BaseAddOut, SPC, MessageEditor):
        self.setSPC(SPC)
        super(QtGui.QGroupBox, self).__init__(parent)
        self.toggled.connect(self.monitorStatus)
        self.ConfigurationData = [Nin, Nout, BaseAddIn, BaseAddOut, 'red']
        self.setTitle("Monitor del PLC")
        self.setCheckable(True)
        self.setChecked(False)
        self.Inputs = []
        self.Outputs = []
        self.PLCLayOut = QtGui.QVBoxLayout(self)
        self.setup(self.ConfigurationData)
        self.setMaximumSize(1000, 250)
        self.MessageEditor = MessageEditor
        
    def updateIndicators(self,inputs,outputs):
        for i in xrange(self.ConfigurationData[0]):
            self.Inputs[i].setSatus(inputs[i])
        for i in xrange(self.ConfigurationData[1]):
            self.Outputs[i].setSatus(outputs[i])
        
    def monitorStatus(self,on):
        if on:
            try:
                self.monitor.reconfigure(self.ConfigurationData,self.SPC,self.MessageEditor.stationNumber())
                self.monitor.start()
            except AttributeError:
                try:
                    self.monitor = RTUMonitor(self.ConfigurationData,self.SPC,self.MessageEditor.stationNumber(),self)
                    self.monitor.coilsRead.connect(self.updateIndicators)
                    self.MessageEditor.enviar.connect(self.monitor.sendMessage)
                    self.monitor.start()
                except modbus_tk.modbus.ModbusError, e:
                    print("%s- Code=%d" % (e, e.get_exception_code())) 
        else:
            try:
                self.monitor.terminate()
            except:
                pass
        
    def setSPC(self,SPC):
        self.SPC = SPC      
        
    def setup(self,ConfigurationData):
        # extrayendo configuración
        Nin = ConfigurationData[0]
        Nout = ConfigurationData[1]
        BaseAddIn = ConfigurationData[2]
        BaseAddOut = ConfigurationData[3]
        color = ConfigurationData[4]
        self.ConfigurationData = ConfigurationData
        for input in self.Inputs: input.close()
        for output in self.Outputs: output.close()
        self.Inputs = []
        self.Outputs = []
        InputLayOut = QtGui.QHBoxLayout()
        OutputLayOut = QtGui.QHBoxLayout()        
        for i in xrange(Nin): 
            self.Inputs.append(DigitalPoint(self,BaseAddIn+i,"I"+str(i+1)))
            self.Inputs[i].setColor(color)
            InputLayOut.addWidget(self.Inputs[i])            
        for i in xrange(Nout): 
            self.Outputs.append(DigitalPoint(self,BaseAddOut+i,"O"+str(i+1)))
            self.Outputs[i].setColor(color)
            OutputLayOut.addWidget(self.Outputs[i])
        if self.PLCLayOut.count()!= 0:
            self.PLCLayOut.removeItem(self.PLCLayOut.itemAt(0))
            self.PLCLayOut.removeItem(self.PLCLayOut.itemAt(0))
        self.PLCLayOut.addLayout(InputLayOut)
        self.PLCLayOut.addLayout(OutputLayOut)
        
class PLCDialog(QtGui.QWidget):
    def __init__(self, ConfigurationData, parent=None):
        super(PLCDialog, self).__init__(parent)
        self.windowTitle = QtCore.QString().fromUtf8("Configuración del PLC")
        self.ConfigurationData = ConfigurationData
        Layout = QtGui.QVBoxLayout(self)
        
        NumInLayout = QtGui.QHBoxLayout()
        Label = QtGui.QLabel('Cantidad de Entradas: ')
        self.NumIn = QtGui.QSpinBox(self)
        self.NumIn.setMaximum(18)
        self.NumIn.setValue(self.ConfigurationData[0])
        NumInLayout.addWidget(Label)
        NumInLayout.addWidget(self.NumIn)
        
        NumOutLayout = QtGui.QHBoxLayout()
        Label = QtGui.QLabel('Cantidad de Salidas: ')
        self.NumOut = QtGui.QSpinBox(self)
        self.NumOut.setMaximum(18)
        self.NumOut.setValue(self.ConfigurationData[1])
        NumOutLayout.addWidget(Label)
        NumOutLayout.addWidget(self.NumOut)
        
        self.BaseInputAddress = AddressInput(self,"Dirección base de las Entradas:", self.ConfigurationData[2])
        self.BaseOutputAddress = AddressInput(self,"Dirección base de las Salidas:", self.ConfigurationData[3])
        
        self.ColorButtonGroup = QtGui.QButtonGroup(self)
        self.red = QtGui.QRadioButton('Rojo')
        if ConfigurationData[4] == 'red': self.red.setChecked(True)
        self.green = QtGui.QRadioButton('Verde')
        if ConfigurationData[4] == 'green': self.green.setChecked(True)
        self.ColorButtonGroup.addButton(self.red)
        self.ColorButtonGroup.addButton(self.green)
        ColorLayOut = QtGui.QHBoxLayout()
        ColorLayOut.addWidget(self.red)
        ColorLayOut.addWidget(self.green)
        
        Layout.addLayout(NumInLayout)
        Layout.addLayout(NumOutLayout)
        Layout.addWidget(self.BaseInputAddress)
        Layout.addWidget(self.BaseOutputAddress)
        Layout.addLayout(ColorLayOut)
        
        self.Dialog = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        Layout.addWidget(self.Dialog)
        self.Dialog.rejected.connect(self.close)
        self.Dialog.accepted.connect(self.ok)    
        
    def ok(self):
        if self.ColorButtonGroup.checkedButton() == self.red:
            color = 'red'
        else:
            color = 'green'
        self.ConfigurationData = [self.NumIn.value(),self.NumOut.value(),self.BaseInputAddress.getValue(),self.BaseOutputAddress.getValue(), color]
        self.emit(QtCore.SIGNAL("ConfigurationChanged"),self.ConfigurationData)
        self.close()
        
class AddressInput(QtGui.QWidget):
    def __init__(self, parent,title,value):
        super(QtGui.QWidget, self).__init__(parent)
        LayOut = QtGui.QHBoxLayout(self)
        Label = QtGui.QLabel(QtCore.QString().fromUtf8(title), self)
        self.Edit = QtGui.QLineEdit(self)
        self.Edit.cursorPositionChanged.connect(self.cursorPlacer)
        self.mask = {"hex":"HHHH","dec":"99999"}
        self.base = QtGui.QComboBox(self)
        self.base.addItems(["dec","hex"])
        self.base.currentIndexChanged.connect(self.setMask)
        self.setMask()
        self.Edit.setText(str(value))
        LayOut.addWidget(Label)
        LayOut.addWidget(self.Edit)
        LayOut.addWidget(self.base)
        
    def cursorPlacer(self):
        if self.Edit.text()=="": self.Edit.setCursorPosition(0)
        
    def setMask(self):
        key = self.base.currentText()
        self.Edit.setInputMask(self.mask[str(key)])
        
    def getValue(self):
        valor = self.Edit.text().toInt()[0]
        if self.base.currentText() == "hex":
            valor = self.Edit.text().toInt(16)[0]
        return valor
        
class DigitalPoint(QtGui.QWidget):
    def __init__(self, parent, Address, Text):
        #---- Constantants ----
        self.ColorRED = "red"
        self.ColorGREEN = "green"
        trueImage = {"red":QtGui.QPixmap(":/light_red.gif"),"green":QtGui.QPixmap(":/light_green.gif")}
        falseImage = {"red":QtGui.QPixmap(":/light_red_off.gif"),"green":QtGui.QPixmap(":/light_green_off.gif")}
        self.Image = {True:trueImage,False:falseImage}
        
        #---- Initializations ----
        super(QtGui.QWidget, self).__init__(parent)
        PointLAyout = QtGui.QVBoxLayout(self)
        self.color = self.ColorRED
        Label = QtGui.QLabel(Text)
        Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Led = QtGui.QLabel("")
        self.Led.setAlignment(QtCore.Qt.AlignCenter)
        #self.Led.mousePressEvent.connect(self.changeStatus)
        self.setSatus(False)
        PointLAyout.addWidget(Label)
        PointLAyout.addWidget(self.Led)
        
    def setSatus(self, Status):
        self.status = Status
        self.Led.setPixmap(self.Image[Status][self.color])
        #self.Led.setText(str(Status))
    
    def setColor(self, Color):
        self.color = Color
        self.setSatus(self.status)
        
    def mousePressEvent(self, ev):
        newStatus = not(self.status)
        self.setSatus(newStatus)
