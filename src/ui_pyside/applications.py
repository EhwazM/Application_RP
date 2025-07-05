from PySide6.QtCore import QUrl, QThread, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QComboBox, QGroupBox,
                               QDoubleSpinBox, QSpinBox, QAbstractSpinBox, QTabWidget, QSizePolicy)
from PySide6.QtGui import QAction
from bokeh.server.server import Server
from bokeh.plotting import figure

from rp_serial.plot_data import SerialPlot

import serial, sys

class Oscilloscope(QMainWindow):
    def __init__(self, app, serialrp_plot: SerialPlot, url='http://localhost:5006/main'):
        super().__init__()
        self.app = app
        self.url = url
        self.serialrp_plot = serialrp_plot
        self.setWindowTitle("Navegador Web Embebido")
        self.create_menu_bar()

        # Widgets

        ## WebEngine (Bokeh Plot)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        ## List of serial ports

        self.ports_list = QComboBox()
        self.ports_list.addItems(self.serialrp_plot.search())

        self.ports_list.textActivated.connect(self.serialrp_plot.select_port)

        self.updt_port_list_button = QPushButton("Update Port list")
        self.updt_port_list_button.pressed.connect(self.update_port_list)

        ## Serial baud-rate

        self.serial_baud_rate_spin = QSpinBox()
        self.serial_baud_rate_spin.setMinimum(0)
        self.serial_baud_rate_spin.setMaximum(int(1e7))
        self.serial_baud_rate_spin.setValue(self.serialrp_plot.data_collect.baudrate)
        self.serial_baud_rate_spin.valueChanged.connect(self.serialrp_plot.update_baud_rate)

        ## Generator 

        self.create_generator_settings()
        self.test_button = QPushButton()
        self.test_button.pressed.connect(self.serialrp_plot.generate_signal)

        ## Min-Max ranges

        self.min_spinbox = QDoubleSpinBox()
        self.min_spinbox.setDecimals(2)
        self.min_spinbox.setSingleStep(0.1)
        self.min_spinbox.setMinimum(-100)
        self.min_spinbox.setValue(self.serialrp_plot.plot_b.y_range.start)
        self.min_spinbox.valueChanged.connect(self.set_y_range_from_spinboxes)

        self.max_spinbox = QDoubleSpinBox()
        self.max_spinbox.setDecimals(2)
        self.max_spinbox.setSingleStep(0.1)
        self.max_spinbox.setMaximum(100)
        self.max_spinbox.setValue(self.serialrp_plot.plot_b.y_range.end)
        self.max_spinbox.valueChanged.connect(self.set_y_range_from_spinboxes)
    
        # Layouts

        self.osci_layout = QVBoxLayout()
        self.osci_layout.addWidget(self.browser)

        self.serial_layout = QVBoxLayout()
        self.serial_layout.addWidget(self.ports_list)
        self.serial_layout.addWidget(self.serial_baud_rate_spin)
        self.serial_layout.addWidget(self.updt_port_list_button)

        self.page1 = QWidget()
        self.page2 = QWidget()

        self.osci_generator_layout_1 = QVBoxLayout(self.page1)
        # self.osci_generator_layout_1.addWidget(self.test_button)
        # self.osci_generator_layout_1.addWidget(self.ch_spinbox_1)
        self.osci_generator_layout_1.addWidget(self.vpp_spinbox_1)
        self.osci_generator_layout_1.addWidget(self.fq_spinbox_1)
        self.osci_generator_layout_1.addWidget(self.wf_combobox_1)

        self.osci_generator_layout_2 = QVBoxLayout(self.page2)
        # self.osci_generator_layout_2.addWidget(self.test_button)
        # self.osci_generator_layout_2.addWidget(self.ch_spinbox_2)
        self.osci_generator_layout_2.addWidget(self.vpp_spinbox_2)
        self.osci_generator_layout_2.addWidget(self.fq_spinbox_2)
        self.osci_generator_layout_2.addWidget(self.wf_combobox_2)

        self.osci_settings_layout = QVBoxLayout()
        self.osci_settings_layout.addWidget(self.min_spinbox)
        self.osci_settings_layout.addWidget(self.max_spinbox)

        # TabWidgets

        self.generator_tabwidget = QTabWidget()
        self.generator_tabwidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        self.generator_tabwidget.addTab(self.page1, "1")
        self.generator_tabwidget.addTab(self.page2, "2")

        # Group Boxes

        self.osci_groupbox = QGroupBox("Oscilloscope")
        self.osci_groupbox.setLayout(self.osci_layout)

        self.serial_groupbox = QGroupBox("Serial Settings")
        self.serial_groupbox.setLayout(self.serial_layout)

        self.osci_generator_groupbox = QGroupBox("Generator Settings")

        self.osci_settings_groupbox = QGroupBox("Oscilloscope settings")
        self.osci_settings_groupbox.setLayout(self.osci_settings_layout)

        # Final Layouts

        self.menu_layout = QVBoxLayout()
        self.menu_layout.addWidget(self.serial_groupbox)
        self.menu_layout.addWidget(self.generator_tabwidget)
        self.menu_layout.addWidget(self.osci_settings_groupbox)
        
        self.central_widget = QWidget()
        self.osci_layout = QHBoxLayout()
        self.osci_layout.addLayout(self.menu_layout)
        self.osci_layout.addWidget(self.osci_groupbox, stretch=1)
        self.central_widget.setLayout(self.osci_layout)
        self.setCentralWidget(self.central_widget)

    def update_port_list(self):
        self.ports_list.clear()
        self.ports_list.addItems(self.serialrp_plot.search())

    def update_generator_values_1(self):
        ch = 1
        vpp = self.vpp_spinbox_1.value()
        fq = self.fq_spinbox_1.value()
        wf = self.wf_combobox_1.currentText()

        self.serialrp_plot.generate_signal(ch=ch, vpp=vpp, fq=fq, wf=wf)

    def update_generator_values_2(self):
        ch = 2
        vpp = self.vpp_spinbox_2.value()
        fq = self.fq_spinbox_2.value()
        wf = self.wf_combobox_2.currentText()

        self.serialrp_plot.generate_signal(ch=ch, vpp=vpp, fq=fq, wf=wf)

    def set_y_range_from_spinboxes(self):
        min_val = self.min_spinbox.value()
        max_val = self.max_spinbox.value()
        self.serialrp_plot.update_y_range(min_val=min_val, max_val=max_val)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu (empty for now)
        edit_menu = menu_bar.addMenu("Edit")
        # You can add future actions here

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        update_ports_action = QAction("Update Ports", self)
        update_ports_action.triggered.connect(self.update_port_list)
        tools_menu.addAction(update_ports_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: print("Oscilloscope app v1.0"))  # Replace with real dialog
        help_menu.addAction(about_action)

    def create_generator_settings(self):
        ## 1
        # self.ch_spinbox_1 = QSpinBox()
        # self.ch_spinbox_1.setSingleStep(1)
        # self.ch_spinbox_1.setMaximum(2)
        # self.ch_spinbox_1.setMinimum(1)
        # self.ch_spinbox_1.setValue(1)
        # self.ch_spinbox_1.valueChanged.connect(self.update_generator_values)

        self.vpp_spinbox_1 = QDoubleSpinBox()
        self.vpp_spinbox_1.setDecimals(1)
        self.vpp_spinbox_1.setSingleStep(0.1)
        self.vpp_spinbox_1.setMaximum(2)
        self.vpp_spinbox_1.setMinimum(0)
        self.vpp_spinbox_1.setValue(1.5)
        self.vpp_spinbox_1.valueChanged.connect(self.update_generator_values_1)

        self.fq_spinbox_1 = QSpinBox()
        self.fq_spinbox_1.setSingleStep(1000)
        self.fq_spinbox_1.setMaximum(int(6.25e7))
        self.fq_spinbox_1.setMinimum(0)
        self.fq_spinbox_1.setValue(int(1e4))
        self.fq_spinbox_1.valueChanged.connect(self.update_generator_values_1)

        self.wf_combobox_1 = QComboBox()
        self.wf_combobox_1.addItems(["sine", "sqr", "tri", "sweep", "dc"])
        self.wf_combobox_1.textActivated.connect(self.update_generator_values_1)

        ## 2

        # self.ch_spinbox_2 = QSpinBox()
        # self.ch_spinbox_2.setSingleStep(1)
        # self.ch_spinbox_2.setMaximum(2)
        # self.ch_spinbox_2.setMinimum(1)
        # self.ch_spinbox_2.setValue(1)
        # self.ch_spinbox_2.valueChanged.connect(self.update_generator_values)

        self.vpp_spinbox_2 = QDoubleSpinBox()
        self.vpp_spinbox_2.setDecimals(1)
        self.vpp_spinbox_2.setSingleStep(0.1)
        self.vpp_spinbox_2.setMaximum(2)
        self.vpp_spinbox_2.setMinimum(0)
        self.vpp_spinbox_2.setValue(1.5)
        self.vpp_spinbox_2.valueChanged.connect(self.update_generator_values_2)

        self.fq_spinbox_2 = QSpinBox()
        self.fq_spinbox_2.setSingleStep(1000)
        self.fq_spinbox_2.setMaximum(int(6.25e7))
        self.fq_spinbox_2.setMinimum(0)
        self.fq_spinbox_2.setValue(int(1e4))
        self.fq_spinbox_2.valueChanged.connect(self.update_generator_values_2)

        self.wf_combobox_2 = QComboBox()
        self.wf_combobox_2.addItems(["sine", "sqr", "tri", "sweep", "dc"])
        self.wf_combobox_2.textActivated.connect(self.update_generator_values_2)
