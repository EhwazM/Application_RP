
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from bokeh.server.server import Server

from threading import Thread
from tornado.ioloop import IOLoop

from rp_serial.plot_data import SerialPlot
import serial

from bokeh.plotting import figure as bk_figure
from bokeh.models import Range1d
from ui_pyside.applications import Oscilloscope

import sys

serial_rp = serial.Serial(baudrate=115200)

p = bk_figure(title="Signal", sizing_mode='stretch_both', x_axis_label='Time (s)', y_axis_label='Voltage (V)', y_range=Range1d(start=-0.5, end=3.5))
    
bokeh_plot = SerialPlot(plot_b=p,
                        n_plots=2,
                        roll_over=1000,
                        colors=['green', 'purple'],
                        update_time=1,
                        scatter_plot=True,
                        oscilloscope_mode=True,
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
    window = Oscilloscope(app, serialrp_plot=bokeh_plot, url='http://localhost:5006')
    window.show()

    sys.exit(app.exec())
