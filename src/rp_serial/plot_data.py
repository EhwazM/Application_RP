import time
import numpy as np

import serial
from serial.tools import list_ports

from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource

class SerialPlot:
    def __init__(self, plot_b, data_collect, n_plots=2, baud_rate=115200 ,roll_over=5000, colors=['red', 'blue', 'green', 'yellow', 'orange', 'purple'], update_time=25, scatter_plot=False, oscilloscope_mode=False):
        self.n_plots = n_plots
        self.plot_b = plot_b
        self.roll_over = roll_over
        self.colors = colors
        self.update_time = update_time
        self.scatter_plot = scatter_plot
        self.osci = oscilloscope_mode
        self.sources = []
        self.lines = []
        self.scatters = []
        self.y = [0.0 for _ in range(n_plots)]

        self.counter = 0
        
        self.baud_rate = baud_rate
        self.data_collect = data_collect
        self.start = time.time()
        self.setup_plot()

    def setup_plot(self):
        for i in range(self.n_plots):
            source = ColumnDataSource(data=dict(x=[], y=[]))
            self.sources.append(source)

            if self.scatter_plot == True:
                scatter = self.plot_b.scatter('x', 'y', source=source, line_color=self.colors[i])
                self.scatters.append(scatter)

            line = self.plot_b.line('x', 'y', source=source, line_color=self.colors[i])
            self.lines.append(line)
        
        print("Setup ready!")

    def attach_doc(self, doc):
        self.doc = doc
        doc.theme = "dark_minimal"
        doc.add_root(self.plot_b)
        if self.osci:
            doc.add_periodic_callback(self.update_oscilloscope, self.update_time)
        else:
            doc.add_periodic_callback(self.update_real_time, self.update_time)


    def update_oscilloscope(self):
            if self.data_collect.is_open:
                print('Starting data recollection.\n')
                data = self.extract_bunch()
                # print('Starting plotting.\n')

                data = np.array(data, dtype=np.float32)
                # print('Works!\n')
                
                x_vals = np.arange(data.shape[0])
                
                for i in range(self.n_plots):
                    try:
                        new_data = dict(x=x_vals, y=data[:, i])
                        self.sources[i].stream(new_data, rollover=data.shape[0])
                    except:
                        print("Data not recognized, skipping plot.")
                        continue
            
            # print('succesful. \n')

    def update_real_time(self):
        if self.data_collect is not None and self.data_collect.is_open:
            while self.data_collect.in_waiting:
                data = self.extract_data()
                
                for i in range(self.n_plots):
                    try:
                        y_temp = float(data[i])
                        end = time.time()
                    except:
                        print("Data not recognized, skipping plot.")
                        continue
                    
                    elapsed_time = end - self.start
                    new_data = dict(x=[elapsed_time], y=[y_temp])

                    self.sources[i].stream(new_data, rollover=self.roll_over)
                    
                self.counter += 1

    def update_y_range(self, min_val=None, max_val=None):
        def _update():
            try:
                if min_val is not None:
                    self.plot_b.y_range.start = min_val
                if max_val is not None:
                    self.plot_b.y_range.end = max_val
                if self.plot_b.y_range.start >= self.plot_b.y_range.end:
                    print("Invalid range: min >= max")
            except Exception as e:
                print(f"Error setting range inside update: {e}")

        if hasattr(self, "doc"):
            self.doc.add_next_tick_callback(_update)
        else:
            print("Document not attached yet.")


    def search(self):
        self.ports = list_ports.comports()

        self.available_ports = [f"{port.device}" for port in self.ports if not port.device.startswith('/dev/ttyS')]

        return self.available_ports

    def extract_data(self):
        serialRecieving = self.data_collect.readline()
        data = serialRecieving.decode('utf-8').rstrip('\n')
        # print(data)
        self.data_serial = data.split(',')

        return self.data_serial

    def extract_bunch(self):
        active = False
        data_bunch = []
        while self.data_collect.in_waiting:
            serialRecieving = self.data_collect.readline()
            data = serialRecieving.decode('utf-8').rstrip('\n')

            if data.startswith('stop') and active:
                active = False
                break
            elif data.startswith('start') and not active:
                active = True
                continue
            
            if active:
                # print(data)
                self.data_serial = data.split(',')
                data_bunch.append(self.data_serial)

        return data_bunch
    
    def select_port(self, port_selected):
        if self.data_collect.is_open:
            self.data_collect.close()
        print(port_selected + " was selected")
        self.data_collect.baudrate=self.baud_rate
        self.data_collect.port = port_selected

        if port_selected != "None":
            self.data_collect.open()

    def update_baud_rate(self, bd):
        if self.data_collect.is_open:
            self.data_collect.close()
        self.data_collect.baudrate = bd
        self.data_collect.open()

    def update_roll_over(self, ro):
        def _update():
            self.roll_over=ro
            
        if hasattr(self, "doc"):
            self.doc.add_next_tick_callback(_update)
        else:
            print("Document not attached yet.")

    def generate_signal(self, ch=1, vpp=1.5, fq=1e4, wf='sine'):
        bash_cmd = f'generate {ch} {vpp} {fq} {wf}'
        self.data_collect.write((bash_cmd + '\n').encode())
        time.sleep(0.1)

        

