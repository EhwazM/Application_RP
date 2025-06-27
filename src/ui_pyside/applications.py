from PySide6.QtCore import QUrl, QThread, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QComboBox, QGroupBox,
                               QDoubleSpinBox, QSpinBox)
from bokeh.server.server import Server
from bokeh.plotting import figure

from rp_serial.plot_data import SerialPlot

class Oscilloscope(QMainWindow):
    def __init__(self, app, serialrp_plot: SerialPlot, url='http://localhost:5006/main'):
        super().__init__()
        self.app = app
        self.url = url
        self.serialrp_plot = serialrp_plot
        self.setWindowTitle("Navegador Web Embebido")

        # Widgets

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        self.ports_list = QComboBox()
        self.ports_list.addItems(self.serialrp_plot.search())

        self.ports_list.textActivated.connect(self.serialrp_plot.select_port)

        self.updt_port_list_button = QPushButton("Update Port list")
        self.updt_port_list_button.pressed.connect(self.update_port_list)

        self.min_range_line = QDoubleSpinBox()
        self.min_range_line.setDecimals(2)
        self.min_range_line.setMinimum(-100)
        self.min_range_line.setValue(self.serialrp_plot.plot_b.y_range.start)
        self.min_range_line.valueChanged.connect(self.set_y_range_from_spinboxes)

        self.max_range_line = QDoubleSpinBox()
        self.max_range_line.setDecimals(2)
        self.max_range_line.setMaximum(100)
        self.max_range_line.setValue(self.serialrp_plot.plot_b.y_range.end)
        self.max_range_line.valueChanged.connect(self.set_y_range_from_spinboxes)

        # Layouts

        self.osci_layout = QVBoxLayout()
        self.osci_layout.addWidget(self.browser)

        self.serial_layout = QVBoxLayout()
        self.serial_layout.addWidget(self.ports_list)
        self.serial_layout.addWidget(self.updt_port_list_button)

        self.osci_settings_layout = QVBoxLayout()
        self.osci_settings_layout.addWidget(self.min_range_line)
        self.osci_settings_layout.addWidget(self.max_range_line)

        # Group Boxes

        self.osci_groupbox = QGroupBox("Oscilloscope")
        self.osci_groupbox.setLayout(self.osci_layout)

        self.serial_groupbox = QGroupBox("Serial Settings")
        self.serial_groupbox.setLayout(self.serial_layout)

        self.osci_settings_groupbox = QGroupBox("Oscilloscope settings")
        self.osci_settings_groupbox.setLayout(self.osci_settings_layout)

        # Final Layouts

        self.menu_layout = QVBoxLayout()
        self.menu_layout.addWidget(self.serial_groupbox)
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

    def set_y_range_from_spinboxes(self):
        min_val = self.min_range_line.value()
        max_val = self.max_range_line.value()
        self.serialrp_plot.update_y_range(min_val=min_val, max_val=max_val)

        
