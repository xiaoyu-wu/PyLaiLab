# Qucik IV

# General Packages

import time
from threading import Thread

import numpy as np


# GUI Related Packages

from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot

from traits.api import *
from traitsui.api import *

# Instrument Packages

import srs830

grey = srs830.SRS830(8)

class Viewer(HasTraits):

    dataset = Instance(ArrayPlotData)
    plot = Instance(Plot)

    def _dataset_default(self):
        x = []
        y = []
        plotdata = ArrayPlotData(x=x, y=y)
        return plotdata

    def _plot_default(self):
        plot = Plot(self.dataset, border_visible=True)
        plot.plot(('x', 'y'), color="red")
        return plot

    def update_display(self, x, y):
        self.dataset.set_data('x', x)
        self.dataset.set_data('y', y)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False,
             width = 300, height = 200, resizable = True)
    )

class MeasureIVThread(Thread):
    def run(self):
        voltages_series = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        new_v = np.array([])
        new_i = np.array([])        
        for voltage in voltages_series:
            if self.wants_abort:
                print "Aborting IV Measurement!"
                break
            else:
                now = time.time()
                grey.set_aux_out(1, voltage)
                new_v = np.append(new_v, voltage)
                new_i = np.append(new_i, grey.get_aux_in(1))
                self.viewer_1.update_display(new_v, new_i)
                elapsed = time.time() - now
                if (1 - elapsed > 0):
                    time.sleep(1 - elapsed)
                else:
                    print "Delay Time Too Small!"
                    self.wants_abort = True
        self.wants_abort = True
        return   
            
class MainWindow(HasTraits):
    viewer_1 = Instance(Viewer, (), label = "IV",)

    measure_iv_thread = Instance(MeasureIVThread)
    btnMeasureIV = Button("MeasureIV")
    def _btnMeasureIV_fired(self):
        if self.measure_iv_thread and self.measure_iv_thread.isAlive():
            self.measure_iv_thread.wants_abort = True
        else:
            print "Start IV Measurement!"
            self.measure_iv_thread = MeasureIVThread()
            self.measure_iv_thread.wants_abort = False
            self.measure_iv_thread.viewer_1 = self.viewer_1
            self.measure_iv_thread.start()
    view = View(Item("viewer_1", style='custom', show_label=True),
                Item("btnMeasureIV", style="custom", show_label=False),
                resizable = True,
                title = "Quick IV by SRS830")    

main = MainWindow()
main.configure_traits()  