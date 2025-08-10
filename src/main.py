from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from bokeh.server.server import Server

from threading import Thread
from tornado.ioloop import IOLoop

from rp_plot.plot_data import SerialPlot
import serial

from bokeh.plotting import figure as bk_figure
from bokeh.models import Range1d
from ui_pyside.applications import Oscilloscope

import sys

dark_theme = """
    QWidget {
        background-color: #2b2b2b;
        color: #dddddd;
        font-family: Segoe UI, sans-serif;
        font-size: 10pt;
    }

    QPushButton {
        background-color: #3c3f41;
        border: 1px solid #5c5c5c;
        border-radius: 4px;
        padding: 6px 12px;
        color: #ffffff;
    }

    QPushButton:hover {
        background-color: #505354;
        border: 1px solid #6c6c6c;
    }

    QPushButton:pressed {
        background-color: #2b2b2b;
        border: 1px solid #787878;
    }

    QCheckBox {
        spacing: 5px;
        color: #dddddd;
    }

    QLineEdit, QTextEdit {
        background-color: #3c3f41;
        border: 1px solid #5c5c5c;
        color: #ffffff;
        border-radius: 4px;
        padding: 5px;
    }

    QProgressBar {
        border: 1px solid #3a3a3a;
        border-radius: 5px;
        background-color: #2e2e2e;
        text-align: center;
        color: #ffffff;
    }

    QProgressBar::chunk {
        background-color: #00c853;
        width: 10px;
        margin: 0.5px;
    }

    QScrollBar:vertical, QScrollBar:horizontal {
        background-color: #2b2b2b;
        border: none;
        margin: 16px 0 16px 0;
    }

    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background-color: #5c5c5c;
        min-height: 20px;
        border-radius: 4px;
    }

    QScrollBar::add-line, QScrollBar::sub-line {
        background: none;
        border: none;
    }

    QTabWidget::pane {
        border-top: 2px solid #3c3f41;
    }

    QTabBar::tab {
        background-color: #2b2b2b;
        color: #b1b1b1;
        padding: 8px 16px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }

    QTabBar::tab:selected {
        background-color: #3c3f41;
        color: #ffffff;
    }

    QTabBar::tab:hover {
        background-color: #444444;
    }

    QListWidget, QComboBox, QListView {
        background-color: #3c3f41;
        color: #dddddd;
        selection-background-color: #007acc;
        selection-color: #ffffff;
        border: 1px solid #5c5c5c;
        border-radius: 4px;
        padding: 5px;
    }

    QListWidget::item:selected,
    QComboBox QAbstractItemView::item:selected {
        background-color: #007acc;  /* Brighter blue */
        color: #ffffff;
    }

    QMenuBar {
        background-color: #2b2b2b;
        color: #dddddd;
        spacing: 3px;
        padding: 4px;
    }

    QMenuBar::item {
        background-color: transparent;
        color: #dddddd;
        padding: 4px 10px;
    }

    QMenuBar::item:selected {
        background-color: #505354;
        color: #ffffff;
    }

    QMenuBar::item:pressed {
        background-color: #3c3f41;
    }

    QMenu {
        background-color: #2b2b2b;
        color: #dddddd;
        border: 1px solid #5c5c5c;
    }

    QMenu::item {
        padding: 6px 24px;
        background-color: transparent;
        color: #dddddd;
    }

    QMenu::item:selected {
        background-color: #505354;
        color: #ffffff;
    }

    QMenu::separator {
        height: 1px;
        background: #5c5c5c;
        margin: 5px 10px;
    }
"""

serial_rp = serial.Serial(baudrate=115200)

p = bk_figure(title="Signal", sizing_mode='stretch_both', x_axis_label='Time (s)', y_axis_label='Voltage (V)', y_range=Range1d(start=-0.5, end=3.5)) # type: ignore
    
bokeh_plot = SerialPlot(plot_b=p,
                        n_plots=2,
                        roll_over=1000,
                        colors=['green', 'purple'],
                        update_time=1,
                        scatter_plot=True,
                        # oscilloscope_mode=True,
                        data_collect=serial_rp
)

def modify_doc(doc, bokeh_plot):
  bokeh_plot.attach_doc(doc)

def start_bokeh_server():
    loop = IOLoop()
    loop.make_current()
    server = Server({'/': lambda doc: modify_doc(doc, bokeh_plot=bokeh_plot)}, io_loop=loop, allow_websocket_origin=["localhost:5006"])
    server.start()
    print("Bokeh server started at http://localhost:5006")
    loop.start()

if __name__ == '__main__':
    Thread(target=start_bokeh_server, daemon=True).start()

    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme)

    window = Oscilloscope(app, serialrp_plot=bokeh_plot, url='http://localhost:5006')
    window.show()

    sys.exit(app.exec())
