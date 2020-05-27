# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore, Qt
import PyQt4.Qwt5 as Qwt
from PLC_digital_IO import RTUMonitor
from numpy.random import rand
from numpy import int16


BASE_ADDRESS = 640 

import sys
import serial

#add logging capability
import logging

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu

class AnalyzerMonitor(QtCore.QThread):
    
    registersRead = QtCore.pyqtSignal(list)
    
    def __init__(self, SPC, stationNumber, parent=None):
        super(AnalyzerMonitor, self).__init__(parent)
        self.reconfigure(SPC,stationNumber)
        
        self.master.set_timeout(5.0)
        self.master.set_verbose(True)
        # Logger
#        self.logger = modbus_tk.utils.create_logger("console")
#        self.logger.info("connected")
        
        # Candado
        self.mutex = QtCore.QMutex()
        
    def reconfigure(self, SPC, stationNumber):
            self.port = str(SPC[0])
            self.baudrate = int(SPC[1])
            self.bytesize = int(SPC[2])
            self.parity = str(SPC[3])
            self.stopbits = int(SPC[4])
            self.xonxoff = int(SPC[5])
            self.stationNumber = stationNumber
            self.master = modbus_rtu.RtuMaster(serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits, xonxoff=self.xonxoff))
        
    def run(self):
        while True:
            self.mutex.lock()
            [VL1n,AL1,WL1,VL2n,AL2,WL2,VL3n,AL3,WL3,VL12,VL31,VL23] = self.master.execute(1, cst.READ_INPUT_REGISTERS, BASE_ADDRESS, 12)
            [VLLs,Amax,An,Ws,VAL1,VAL2,VAL3,VAs,varL1,varL2,varL3,vars] = self.master.execute(1, cst.READ_INPUT_REGISTERS, BASE_ADDRESS+24, 12)
            [Wdmd,VAdmd,Wdmdmax,none,Hz,Admdmax,PF1,PF2] = self.master.execute(1, cst.READ_INPUT_REGISTERS, BASE_ADDRESS+48, 8)
            self.mutex.unlock()
            PFL2 = self.pfFilter(PF1/0xff)
            PFL1 = self.pfFilter(PF1.__and__(0xff))
            PFs = self.pfFilter(PF2/0xff)
            PFL3 = self.pfFilter(PF2.__and__(0xff))
            sys = [VLLs,25*An/1000.,int16(25*Ws),int16(25*vars),PFs/100.]
            fase1 = [VL1n/10.,25*AL1/1000.,int16(25*WL1/10.),int16(25*varL1/10),PFL1/100.]
            fase2 = [VL2n/10.,25*AL2/1000.,int16(25*WL2/10.),int16(25*varL2/10),PFL2/100.]
            fase3 = [VL3n/10.,25*AL3/1000.,int16(25*WL3/10.),int16(25*varL3/10),PFL3/100.]
            meassurements = [sys,fase1,fase2,fase3]
            self.registersRead.emit(meassurements)
            self.msleep(1000) #ms
    
    def sendMessage(self, Message):
        self.mutex.lock()
        response =  self.master.execute(Message[0],Message[1],Message[2],Message[3])
        self.mutex.unlock()
    
    def pfFilter(self, pf):
        neg = pf/0x7f
        pf = pf.__and__(0x7f)
        if neg:
            pf *= -1
        return pf
        
class Meter(Qwt.QwtDial):
    # __init__()
    def __init__(self,label,*args):
        Qwt.QwtDial.__init__(self, *args)
        self.__label = label
        self.setWrapping(False)
        self.setReadOnly(True)

        self.setOrigin(135.0)
        self.setScaleArc(0.0, 270.0)

        self.setNeedle(Qwt.QwtDialSimpleNeedle(
            Qwt.QwtDialSimpleNeedle.Arrow,
            True,
            Qt.QColor(QtCore.Qt.red),
            Qt.QColor(QtCore.Qt.gray).light(130)))

        self.setScaleOptions(Qwt.QwtDial.ScaleTicks | Qwt.QwtDial.ScaleLabel)
        self.setScaleTicks(0, 4, 8)
        self.setPalette(self.__colorTheme(Qt.QColor(Qt.Qt.darkGray).dark(150)))
        
    def __colorTheme(self, base):
        background = base.dark(150)
        foreground = base.dark(200)
        
        mid = base.dark(110)
        dark = base.dark(170)
        light = base.light(170)
        text = foreground.light(800)

        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Base, base)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Background, background)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Mid, mid)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Light, light)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Dark, dark)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Text, text)
        palette.setColor(Qt.QPalette.Active, Qt.QPalette.Foreground, foreground)
        
        return palette
    
    # drawScaleContents
    def drawScaleContents(self, painter, center, radius):
        rect = Qt.QRect(0, 0, 2 * radius, 2 * radius - 10)
        rect.moveCenter(center)
        painter.setPen(self.palette().color(Qt.QPalette.Text))
        painter.drawText(
            rect, Qt.Qt.AlignBottom | Qt.Qt.AlignHCenter, self.__label)
        
class AnalogInstrument(QtGui.QWidget):
    def __init__(self, parent, label, units, rango, digits):
        super(QtGui.QWidget, self).__init__(parent)
        LayOut = QtGui.QGridLayout(self)
        self.label = QtGui.QLabel(QtCore.QString().fromUtf8(label))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        maximo = QtGui.QLabel("Max")
        self.upperRange = QtGui.QLineEdit(self)
        self.upperRange.setInputMask("999")
        self.upperRange.setText(str(rango[1]))
        self.upperRange.textChanged.connect(self.setUpperRange)
        self.upperRange.setMaximumSize(35,25)
        h = QtGui.QHBoxLayout()
        h.addWidget(maximo)
        h.addWidget(self.upperRange)
        self.range = rango
        self.meter = Meter(units,self)
        self.setUpperRange(rango[1])
        self.digital = DigitalInstrument("",units,digits)
        LayOut.addWidget(self.label,0,0)
        LayOut.addLayout(h,1,0)
        LayOut.addWidget(self.digital,2,0)
        LayOut.addWidget(self.meter,0,1,3,1)
    
    def setLabel(self,text):
        self.label.setText(QtCore.QString().fromUtf8(text))
        
    def setValue(self,value):
        self.digital.digital.display(value)
        self.meter.setValue(value)
        
    def setUpperRange(self,limit):
        rango = self.range
        rango[1] = int(limit)
        self.meter.setRange(rango[0], rango[1])
        self.meter.setScale(-1, 2, (rango[1]-rango[0])/10.)
        self.meter.setEnabled(False)
        self.meter.setEnabled(True)
        
        
class DigitalInstrument(QtGui.QWidget):
    def __init__(self, label, units, digits):
        super(QtGui.QWidget, self).__init__()
        LayOut = QtGui.QHBoxLayout(self)
        label = QtGui.QLabel(QtCore.QString().fromUtf8(label))
        self.digital = QtGui.QLCDNumber(digits,self)
        self.setPallete()
        unit = QtGui.QLabel(units)
        LayOut.addWidget(label)
        LayOut.addWidget(self.digital)
        LayOut.addWidget(unit)
        
    def setPallete(self):
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Active,Qt.QPalette.WindowText,Qt.QColor(Qt.Qt.red))
        palette.setColor(Qt.QPalette.Active,Qt.QPalette.Button,Qt.QColor(Qt.Qt.black))
        #palette.setColor(Qt.QPalette.Inactive,Qt.QPalette.WindowText,Qt.QColor(Qt.Qt.red))
        #palette.setColor(Qt.QPalette.Inactive,Qt.QPalette.Button,Qt.QColor(Qt.Qt.black))
        self.digital.setPalette(palette)
        
    def setValue(self,value):
        self.digital.display(value)
        
class MeasurementPanel(QtGui.QWidget):
    def __init__(self, parent):
        super(QtGui.QWidget, self).__init__(parent)
        LayOut = QtGui.QHBoxLayout(self)
        self.VoltMeter = AnalogInstrument(self, "Tensión", "V", [0,250], 4)
        self.AmpMeter = AnalogInstrument(self, "Corriente", "A", [0,5], 4)
        v = QtGui.QVBoxLayout()
        self.Pa = DigitalInstrument("Pa: ", "W", 4)
        self.Q = DigitalInstrument("Q: ", "VAR", 4)
        self.pf =  DigitalInstrument("pf: ", "", 5)
        v.addWidget(self.Pa)
        v.addWidget(self.Q)
        v.addWidget(self.pf)
        LayOut.addWidget(self.VoltMeter)
        LayOut.addWidget(self.AmpMeter)
        LayOut.addLayout(v)
        
    def updateMeassurements(self,(Voltaje, Corriente, Pa, Q, Pf)):
        self.VoltMeter.setValue(Voltaje)
        self.AmpMeter.setValue(Corriente)
        self.Pa.setValue(Pa)
        self.Q.setValue(Q)
        self.pf.setValue(Pf)
        
class Analyzer(QtGui.QGroupBox):    
    messaged = QtCore.pyqtSignal(str)
    def __init__(self, parent, SPC, MessageEditor):
        super(QtGui.QGroupBox, self).__init__(parent)
        self.setSPC(SPC)
        self.MessageEditor = MessageEditor
        self.setTitle("Analizador de Redes")
        self.setCheckable(True)
        self.setChecked(False)
        self.tab = QtGui.QTabWidget(self)
        self.system = MeasurementPanel(self)
        self.system.VoltMeter.setLabel("Tensión de Línea")
        self.system.AmpMeter.setLabel("Corriente de Neutro")
        self.phase1 = MeasurementPanel(self)
        self.phase2 = MeasurementPanel(self)
        self.phase3 = MeasurementPanel(self)
        self.tab.addTab(self.system,"Sistema")
        self.tab.addTab(self.phase1,"Fase 1")
        self.tab.addTab(self.phase2,"Fase 2")
        self.tab.addTab(self.phase3,"Fase 3")
        self.tab.setTabPosition(self.tab.East)
        LayOut = QtGui.QVBoxLayout(self)
        LayOut.addWidget(self.tab)
        self.toggled.connect(self.monitorStatus)
        self.setMaximumSize(1000, 250)
        
    def setSPC(self,SPC):
        self.SPC = SPC

    def updateIndicators(self,meassurements):
        self.system.updateMeassurements(meassurements[0])
        self.phase1.updateMeassurements(meassurements[1])
        self.phase2.updateMeassurements(meassurements[2])
        self.phase3.updateMeassurements(meassurements[3])
        
    def monitorStatus(self,on):
        if on:
            try:
                self.monitor.reconfigure(self.SPC,self.MessageEditor.stationNumber())
                self.monitor.start()
            except AttributeError:
                try:
                    self.monitor = AnalyzerMonitor(self.SPC,self.MessageEditor.stationNumber(),self)
                    self.monitor.registersRead.connect(self.updateIndicators)
                    self.MessageEditor.enviar.connect(self.monitor.sendMessage)
                    self.monitor.start()
                except modbus_tk.modbus.ModbusError, e:
                    print("%s- Code=%d" % (e, e.get_exception_code())) 
        else:
            try:
                self.monitor.terminate()
            except:
                pass
            
    def emitMessage(self,message):
        self.messaged.emit(message)
        
                 
