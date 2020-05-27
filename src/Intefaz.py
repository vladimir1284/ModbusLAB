# -*- coding: utf-8 -*-

#
# Created: Fri Jul  9 14:05:17 2012
#      by: Vladímir Rodríguez Diez
#
from PyQt4 import QtGui, QtCore
from MainWidget import MyMainWidget
from PLC_digital_IO import PLCDialog
#import helpform
#import qrc_resources
progname = "ModbusLab"
progversion = "0.1"


class ApplicationWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("ModbusLab")
		self.resize(1024, 700)
		#---- Menu ----
		self.file_menu = QtGui.QMenu('&Archivo', self)
		self.file_menu.addAction('&Abrir ...', self.fileOpen,
									QtCore.Qt.CTRL + QtCore.Qt.Key_O)
		self.file_menu.addAction('&Guardar ...', self.fileSave,
									QtCore.Qt.CTRL + QtCore.Qt.Key_G)
		self.file_menu.addSeparator()
		self.inform = self.file_menu.addAction('&Informe ...', self.informe,
									QtCore.Qt.CTRL + QtCore.Qt.Key_I)
		self.file_menu.addSeparator()
		self.file_menu.addAction('&Cerrar', self.fileQuit,
									QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
		self.menuBar().addMenu(self.file_menu)

		self.toolsMenu = QtGui.QMenu("&Herramientas", self)
		self.menuBar().addMenu(self.toolsMenu)
		self.toolsMenu.addAction("Con&figurar PLC...", self.plcConfig)
		#TODO Añadir los submenú para conversor de base numérica y Selector de plc

		self.help_menu = QtGui.QMenu('A&yuda', self)
		self.menuBar().addSeparator()
		self.menuBar().addMenu(self.help_menu)

		self.help_menu.addAction('&Acerca ...', self.about)
		#---- Main Widget ----
		#scrollArea = QtGui.QScrollArea()
		#scrollArea.setWidget()
		self.main_widget = MyMainWidget(self)
		self.setCentralWidget(self.main_widget)
		#self.inform.setEnabled(False)
		#---- Status bar ----
		self.statusBar().showMessage("Listo para la entrada de datos!")
		#print self.size()
	#---- Menu Actions ----	
	def fileQuit(self):
		self.close()
		
	def fileOpen(self):
		f = open(self.main_widget.getFileName('Abrir Fichero de Mediciones','dlc'),'r')
		# Tipo de dato
		tipo = f.readline().split(': ')[1].split('\n')[0]
		# Seleccionar practica en cuetion
		if tipo == 'MotorCD':
			self.selectMotor()
			self.main_widget.fileOpen(f)
		else:
			if tipo == 'GeneradorCD':
				self.selectGenerador()
				self.main_widget.fileOpen(f)
			else:
				if tipo == 'Convertidor':
					self.selectConvertidor()
					self.main_widget.fileOpen(f)

	def plcConfig(self):
		self.id = PLCDialog(self.main_widget.PLCMonitor.ConfigurationData)
		self.id.connect(self.id, QtCore.SIGNAL("ConfigurationChanged"),self.main_widget.PLCMonitor.setup)
		self.id.show()
	
	def fileSave(self):
		self.main_widget.fileSave()
	
	def informe(self):
		self.main_widget.informe()

	def closeEvent(self, ce):
		self.fileQuit()		

	def about(self):
		QtGui.QMessageBox.about(self, "About %s" % progname,
	u"""%(prog)s version %(version)s
Copyleft 2012 Vladimir Rodriguez

Este es un software para el estudio del protocolo 
MODBUS en sus variantes serie y TCP/IP. Fue 
desarrollado con QT para la interfaz gráfica y 
modbus-tk para el manejo del protocolo.

Puede ser usado y modificado sin restricciones;
copias originales asi como modificadas pueden ser
distibuidas sin limitaciones."""
	% {"prog": progname, "version": progversion})
	
