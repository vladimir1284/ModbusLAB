# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore, Qt
from PLC_digital_IO import PLCdigitalIO
from Analyzer import Analyzer
from cStringIO import StringIO
import modbus_tk
import sys

class MyMainWidget(QtGui.QTabWidget):
	def __init__(self,parent):
		QtGui.QWidget.__init__(self,parent)
		#---- Tab ----
		self.currentChanged.connect(self.disableLogger)
		self.setTabPosition(self.West)
		#++++ Bits Operations ++++
		self.RTU_bits = QtGui.QWidget(self)
		self.RTU_registers = QtGui.QWidget(self)
		
		#---- Output Consoles ----
		self.ConsoleWidget = ConsoleWidget(self)
		self.ConsoleWidget1 = ConsoleWidget(self)
				
		#==== Message Editor ====
		self.MessageWidget = MessageEditor(self)
		self.MessageWidget.redirect.connect(self.ConsoleWidget.redirect)
		self.MessageWidget1 = MessageEditor(self)
		self.MessageWidget1.redirect.connect(self.ConsoleWidget1.redirect)
				
		#==== Serial Port Configurator ====
		self.SPCWidget = SerialPortConfiguration(self)
		self.SPCWidget1 = SerialPortConfiguration(self)
		
		#==== PLC Monitor ====
		self.PLCMonitor = PLCdigitalIO(self,18,12,0,64,self.SPCWidget.getSPC(),self.MessageWidget)
		self.connect(self.SPCWidget, QtCore.SIGNAL("ConfigurationChanged"),self.PLCMonitor.setSPC)
		
		#==== Analizador ====
		self.Analizador = Analyzer(self,self.SPCWidget1.getSPC(),self.MessageWidget1)
		self.connect(self.SPCWidget1, QtCore.SIGNAL("ConfigurationChanged"),self.Analizador.setSPC)
		
		#---- LayOut ----
		l = QtGui.QGridLayout(self.RTU_bits)
		l.setVerticalSpacing(3)
		l1 = QtGui.QGridLayout(self.RTU_registers)
		l1.setVerticalSpacing(3)
		#---- Add elements ----
		l.addWidget(self.MessageWidget,0,0,1,-1)
		l.addWidget(self.SPCWidget, 1, 0)
		l.addWidget(self.ConsoleWidget, 1, 1)
		l.addWidget(self.PLCMonitor,2,0,1,2)
		
		l1.addWidget(self.MessageWidget1,0,0,1,-1)
		l1.addWidget(self.SPCWidget1, 1, 0)
		l1.addWidget(self.ConsoleWidget1, 1, 1)
		l1.addWidget(self.Analizador,2,0,1,2)
		
		self.addTab(self.RTU_bits, "Bits operations")
		self.addTab(self.RTU_registers, "Registers operations")

		self.setFocus()
		# Logger
		self.logger = modbus_tk.utils.create_logger("console")
		self.logger.info("connected")
		
	def getFileName(self,titulo,ext):    
		options = QtGui.QFileDialog.Options()
		fileName = QtGui.QFileDialog.getSaveFileName(self,
				titulo,
				'',
				"Ficheros Texto (*."+ext+")")
		if fileName:
			tozos = fileName.split('.')
			if tozos[tozos.__len__()-1] != ext:
				fileName += '.'+ ext
			return fileName
			
	def fileSave(self):
		#TODO enviar mensaje de aviso sobre borrado
		pass
	def fileOpen(self):
		pass
	def informe(self):
		nombre = self.getFileName('Guardar Informe','txt')
		fichero = file(nombre,'w')
		try:
			fichero.write('================================================\n')
			fichero.write('======== Informe generado por ModbusLab ========\n')
			fichero.write('================================================\n\n')
			fichero.write('================================================\n')
			fichero.write('============== Analizador de Redes =============\n')
			fichero.write('================================================\n')
			fichero.write(self.ConsoleWidget1.getText())
			fichero.write('\n================================================\n')
			fichero.write('====================== PLC =====================\n')
			fichero.write('================================================\n')
			fichero.write(self.ConsoleWidget.getText())
		finally:
			fichero.close()
			
	def disableLogger(self):
		self.PLCMonitor.setChecked(False)
		try:
			self.PLCMonitor.monitor.terminate()
		except:
			pass		
		try:
			self.Analizador.monitor.terminate()
		except:
			pass
		self.Analizador.setChecked(False)	
				

class ConsoleWidget(QtGui.QWidget):
	def __init__(self, parent):
		super(QtGui.QWidget, self).__init__(parent)
		ConsoleLayOut = QtGui.QVBoxLayout(self)	
		message_label = QtGui.QLabel("Message Console", self)		
		self.Message_log = QtGui.QPlainTextEdit()
		ConsoleLayOut.addWidget(message_label)
		ConsoleLayOut.addWidget(self.Message_log)
		self.setMaximumSize(600, 200)
	
	def redirect(self, on):
		if on:
			self.old_stdout = sys.stdout
			sys.stdout = self
		else:
			sys.stdout = self.old_stdout
		
	def write(self, txt):
		self.Message_log.appendPlainText(str(txt))
		self.Message_log.moveCursor(QtGui.QTextCursor.End)
	
	def getText(self):
		return self.Message_log.toPlainText()
		
class DataWidget(QtGui.QWidget):
	DIGITAL_WRITE = {0xff00:1,0x0000:0}
	buttonPressed = QtCore.pyqtSignal()
	def __init__(self, parent):
		super(QtGui.QWidget, self).__init__(parent)
		DataLayOut = QtGui.QGridLayout(self)
		DataLabel = QtGui.QLabel("Datos", self)
		self.DataCombo = QtGui.QComboBox(self)
		self.DataButton = QtGui.QPushButton("Editar")
		self.DataButton.pressed.connect(self.buttonPressed.emit)
		DataLayOut.addWidget(DataLabel,0,0,1,2)
		DataLayOut.addWidget(self.DataCombo,1,0)
		DataLayOut.addWidget(self.DataButton,1,1)
		self.DataStatus = {0:True,1:False,2:False,3:False,4:False,5:True,6:True,7:False,8:True,11:False,15:True,16:True}
		self.DataMasks = {0:"HHHH",1:"HHHH",2:"HHHH",3:"HHHH",4:"HHHH",5:"HHHH",6:"HHHH",7:"HHHH",8:"HHHH",11:"HHHH",15:"BBBBBBBB",16:"HHHH"}
		
	def append(self,text):
		self.DataCombo.addItem(text, userData=QtCore.QVariant())
		
	def isReady(self):
		ready = False
		if self.DataCombo.currentText() != '': ready = True
		return ready

	def getValue(self):
		text = self.DataCombo.currentText()
		val = text.toInt(16)[0]
		try:
			val = self.DIGITAL_WRITE[val]
		except:
			pass			
		return val
	
	def clear(self):
		self.DataCombo.clear()
	
	def Enabled(self,value):
		self.setEnabled(self.DataStatus[value])
		self.DataCombo.clear()
		
class MessageEditor(QtGui.QGroupBox):
	enviar = QtCore.pyqtSignal(list)
	redirect = QtCore.pyqtSignal(bool)
	def __init__(self, parent):
		super(QtGui.QGroupBox, self).__init__(parent)
		self.setTitle("Editor de Mensajes")
		self.ConsoleWidget = ConsoleWidget
		MessageLayOut = QtGui.QGridLayout(self)
		MessageLayOut.setVerticalSpacing(3)
		self.setMaximumSize(1000, 180)
		
		#---- Station ---
		self.StationWidget = QtGui.QWidget()
		StationLayOut = QtGui.QVBoxLayout(self.StationWidget)
		StationLabel = QtGui.QLabel(QtCore.QString().fromUtf8("Estación"), self.StationWidget)
		self.StationCombo = QtGui.QComboBox(self.StationWidget)
		for i in xrange(6):
			self.StationCombo.addItem(str(i), userData=QtCore.QVariant(i))
		StationLayOut.addWidget(StationLabel)
		StationLayOut.addWidget(self.StationCombo)
		
		#---- Function ----
		self.FunctionWidget = QtGui.QWidget()
		FunctionLayOut = QtGui.QVBoxLayout(self.FunctionWidget)
		FunctionLabel = QtGui.QLabel(QtCore.QString().fromUtf8("Función"), self.FunctionWidget)
		self.FunctionCombo = QtGui.QComboBox(self.FunctionWidget)
		#Funciones
		self.FunctionCombo.addItem('0 - Control de estaciones esclavas', userData=QtCore.QVariant(0))
		self.FunctionCombo.addItem('1 - Lectura de n bits de salida o internos', userData=QtCore.QVariant(1))
		self.FunctionCombo.addItem('2 - Lectura de n bits de entradas', userData=QtCore.QVariant(2))
		self.FunctionCombo.addItem('3 - Lectura de n palabras de salidas o internos', userData=QtCore.QVariant(3))
		self.FunctionCombo.addItem('4 - Lectura de n palabras de entradas', userData=QtCore.QVariant(4))
		self.FunctionCombo.addItem('5 - Escritura de un bit', userData=QtCore.QVariant(5))
		self.FunctionCombo.addItem('6 - Escritura de una palabra', userData=QtCore.QVariant(6))
		self.FunctionCombo.addItem(QtCore.QString().fromUtf8('7 - Lectura rápida de 8 bits'), userData=QtCore.QVariant(7))
		self.FunctionCombo.addItem(QtCore.QString().fromUtf8('8 - Control de contadores de diagnósticos número 1 a 8'), userData=QtCore.QVariant(8))
		self.FunctionCombo.addItem(QtCore.QString().fromUtf8('11 - Control del contador de diagnósticos número 9'), userData=QtCore.QVariant(11))
		self.FunctionCombo.addItem('15 - Escritura de n bits', userData=QtCore.QVariant(15))
		self.FunctionCombo.addItem('16 - Escritura de n palabras', userData=QtCore.QVariant(16))
		self.FunctionCombo.currentIndexChanged.connect(self.messageFunction)
		FunctionLayOut.addWidget(FunctionLabel)
		FunctionLayOut.addWidget(self.FunctionCombo)
		
		#---- SubFun ---
		self.SubFunWidget = HexInput(self,"SubFunción",4)
		self.SubFunStatus = {0:True,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:True,11:False,15:False,16:False}
		
		#---- Address ---
		self.AddressWidget = HexInput(self,"Dirección",4)
		self.AddressStatus = {0:False,1:True,2:True,3:True,4:True,5:True,6:True,7:False,8:False,11:False,15:True,16:True}
		
		#---- Number ---
		self.NumberWidget = HexInput(self,"Número",4)
		self.NumberStatus = {0:False,1:True,2:True,3:True,4:True,5:False,6:False,7:False,8:False,11:False,15:True,16:True}
		
		#---- Bytes ---
		self.OctetosWidget = HexInput(self,"Octetos",2)
		self.OctetosStatus = {0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,11:False,15:True,16:True}
		
		#---- Data ---
		self.DataWidget = DataWidget(self)
		self.DataWidget.buttonPressed.connect(self.openInputDialog)
		self.DataLen = 1
		
		# Enviar
		self.SendButton = QtGui.QPushButton("Enviar")
		self.SendButton.setEnabled(False)
		self.SendButton.pressed.connect(self.sendMessage)
		
		MessageLayOut.addWidget(self.StationWidget,0,0)
		MessageLayOut.addWidget(self.FunctionWidget,0,1)
		MessageLayOut.addWidget(self.SubFunWidget,0,2)
		MessageLayOut.addWidget(self.AddressWidget,0,3)
		MessageLayOut.addWidget(self.NumberWidget,1,0)
		MessageLayOut.addWidget(self.OctetosWidget,1,1)
		MessageLayOut.addWidget(self.DataWidget,1,2)
		MessageLayOut.addWidget(self.SendButton,1,3)
		
		self.messageFunction()
		self.SubFunWidget.modified.connect(self.isReady)
		self.AddressWidget.modified.connect(self.isReady)
		self.NumberWidget.modified.connect(self.isReady)
		self.OctetosWidget.modified.connect(self.isReady)
		
	
	def sendMessage(self):
		# Redirecciona la salida estándar y emite el mensaje.
		self.redirect.emit(True)
		self.enviar.emit(self.Message)
		self.redirect.emit(False)
	
	def isEmpty(self, widget):
		vacio = widget.getText() == ""
		if vacio:
			self.SendButton.setEnabled(False)
		return vacio
		
	def isReady(self):
		# Preguntar si los elementos estan activos y listos. Luego su valor es añadido al
		# mensage y activado el botón de enviar.
		Message = [self.stationNumber(),self.functionNumber()]
		
		ready = True
		ready *= not(self.SubFunWidget.isEnabled()) or (not(self.isEmpty(self.SubFunWidget)))
		if self.SubFunWidget.isEnabled():
			Message.append(self.SubFunWidget.getValue())
		ready *= not(self.AddressWidget.isEnabled()) or (not(self.isEmpty(self.AddressWidget)))
		if self.AddressWidget.isEnabled():
			Message.append(self.AddressWidget.getValue())
		ready *= not(self.NumberWidget.isEnabled()) or (not(self.isEmpty(self.NumberWidget)))
		if self.NumberWidget.isEnabled():
			Message.append(self.NumberWidget.getValue())
		ready *= not(self.OctetosWidget.isEnabled()) or (not(self.isEmpty(self.OctetosWidget)))
		if self.OctetosWidget.isEnabled():
			Message.append(self.OctetosWidget.getValue())
		ready *= not(self.DataWidget.isEnabled()) or (self.DataWidget.isReady())
		if self.DataWidget.isEnabled():
			Message.append(self.DataWidget.getValue())
			print Message
		
		if ready:
			self.Message =  Message
			self.SendButton.setEnabled(ready)
		
	def stationNumber(self):
		return QtCore.QString.toInt(self.StationCombo.currentText())[0]
	
	def functionNumber(self):
		fun  = self.FunctionCombo.itemData(self.FunctionCombo.currentIndex(), role=QtCore.Qt.UserRole)
		return fun.toInt()[0]
		
	def messageFunction(self):
		value = self.functionNumber()
		self.AddressWidget.setEnabled(self.AddressStatus[value])
		self.SubFunWidget.setEnabled(self.SubFunStatus[value])
		self.NumberWidget.setEnabled(self.NumberStatus[value])
		self.OctetosWidget.setEnabled(self.OctetosStatus[value])
		self.DataWidget.Enabled(value)
		self.DataMask = self.DataWidget.DataMasks[value]
	
	def setDataLen(self):
		text = self.NumberWidget.Edit.text()
		self.DataLen = text.toInt(16)[0]
	
	def openInputDialog(self):
		len = self.DataLen
		if self.DataMask == "BBBBBBBB": len = self.OctetosWidget.Edit.text().toInt(16)[0]
		self.id = DataInputDialog(self.DataMask,len)
		self.id.connect(self.id, QtCore.SIGNAL("ValueChanged"),self.setData)
		self.id.show()
		
	def setData(self,par):
		self.DataWidget.clear()
		for LineEdit in par:
			self.DataWidget.append(LineEdit.text())
		self.isReady()
			
class HexInput(QtGui.QWidget):
	modified = QtCore.pyqtSignal()
	def __init__(self, parent,title,len):
		super(QtGui.QWidget, self).__init__(parent)
		LayOut = QtGui.QVBoxLayout(self)
		Label = QtGui.QLabel(QtCore.QString().fromUtf8(title), self)
		self.Edit = QtGui.QLineEdit(self)
		self.Edit.cursorPositionChanged.connect(self.cursorPlacer)
		self.Edit.textChanged.connect(self.modified.emit)
		self.Edit.textChanged.connect(self.updateToolTip)
		mask = "HHHH"
		self.Edit.setInputMask(mask[0:len])
		LayOut.addWidget(Label)
		LayOut.addWidget(self.Edit)
		self.setToolTip('Esto es una entrada hexadecimal')
		
	def updateToolTip(self):
		self.setToolTip('El valor decimal es: ' + str(self.getValue()))
		
	def cursorPlacer(self):
		if self.Edit.text()=="": self.Edit.setCursorPosition(0)
		#self.modified.emit()
		
	def getText(self):
		return self.Edit.text()
	
	def getValue(self):
		texto = self.getText()
		return texto.toInt(16)[0]
		
class DataInputDialog(QtGui.QWidget):
	def __init__(self, Mask, len, parent=None):
		super(DataInputDialog, self).__init__(parent)
		self.inputList = []
		Layout = QtGui.QVBoxLayout(self)
		Label = QtGui.QLabel('Datos a enviar',self)
		Layout.addWidget(Label)
		for i in xrange(len):
			self.inputList.append(QtGui.QLineEdit(self))
			Layout.addWidget(self.inputList[i])
			self.inputList[i].setInputMask(Mask)
			self.inputList[i].textChanged.connect(self.enebleOk)
		self.Dialog = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
		self.Dialog.button(self.Dialog.Ok).setEnabled(False)
		Layout.addWidget(self.Dialog)
		self.Dialog.rejected.connect(self.close)
		self.Dialog.accepted.connect(self.ok)
		
	def enebleOk(self):
		Enable = True
		for LineEdit in self.inputList:
			Enable *= (LineEdit.text() != "")
		self.Dialog.button(self.Dialog.Ok).setEnabled(Enable)
				
		
	def ok(self):
		self.emit(QtCore.SIGNAL("ValueChanged"),self.inputList)
		self.close()
		
class SerialPortConfiguration(QtGui.QGroupBox):
	
	def __init__(self, parent):
		super(QtGui.QGroupBox, self).__init__(parent)
		self.setTitle(QtCore.QString().fromUtf8("Configuración del Puerto Serie"))
		SPCLayOut = QtGui.QGridLayout(self)
		self.Port = SerialConfigInput("Port",['/dev/ttyUSB0','/dev/ttyS0'])
		self.baudrate = SerialConfigInput("BaudRate",["1200","2400","4800","9600","19200","38400","57600"])
		self.baudrate.Combo.setCurrentIndex(3)
		self.bytesize = SerialConfigInput("ByteSize",["7","8"])
		self.bytesize.Combo.setCurrentIndex(1)
		self.parity = SerialConfigInput("Parity",["odd","even","N"])
		self.parity.Combo.setCurrentIndex(2)
		self.stopbits = SerialConfigInput("StopBits",["0","1","2"])
		self.stopbits.Combo.setCurrentIndex(1)
		self.xonxoff = SerialConfigInput("XonXoff",["0","1"])
		self.xonxoff.Combo.setCurrentIndex(0)
		self.Port.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		self.baudrate.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		self.bytesize.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		self.parity.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		self.stopbits.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		self.xonxoff.Combo.currentIndexChanged.connect(self.ConfigurationChanged)
		SPCLayOut.addWidget(self.Port,0,0)
		SPCLayOut.addWidget(self.baudrate,1,0)
		SPCLayOut.addWidget(self.bytesize,2,0)
		SPCLayOut.addWidget(self.parity,0,1)
		SPCLayOut.addWidget(self.stopbits,1,1)
		SPCLayOut.addWidget(self.xonxoff,2,1)
		self.SPC = self.getSPC()
		self.setMaximumSize(350, 200)
	def getSPC(self):
		return(self.Port.getValue(),self.baudrate.getValue(),self.bytesize.getValue(),self.parity.getValue(),self.stopbits.getValue(),self.xonxoff.getValue())
	
	def ConfigurationChanged(self):
		self.SPC = self.getSPC()
		self.emit(QtCore.SIGNAL("ConfigurationChanged"),self.SPC)
		
		
class SerialConfigInput(QtGui.QWidget):
	def __init__(self, title, options, parent=None):
		super(SerialConfigInput, self).__init__(parent)
		LayOut = QtGui.QHBoxLayout(self)
		Label = QtGui.QLabel(title, self)
		self.Combo = QtGui.QComboBox(self)
		self.Combo.addItems(options)
		LayOut.addWidget(Label)
		LayOut.addWidget(self.Combo)
		
	def getValue(self):
		return self.Combo.currentText()
	
