import time
from threading import Thread

import numpy as np

from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot

from traits.api import *
from traitsui.api import *

import k2634b

# Instruments
longbox = k2634b.K2634B(26)
#longbox.reset()

# Pop up a window for Training Settings
class Settings(HasTraits):
    V_ds = Float(0.01, label = "Source-Drain Voltage (V)")
    I_ds_limit = Float(10, label = "Source-Drain Current Limit (nA)")
    V_high = Float(1.0, label = "High-end Gate Voltage (V)")
    V_low = Float(0, label ="Low-end Gate Voltage (V)")
    I_g_limit = Float(10, label = "Leakage/Gate Current Limit (nA)")
    step_size = Float(1, label = "Ramp Step Size (mV)")
    delay = Float(0.5, label = "Delay Time (s)")    
    cycles = Int(1, label = "Number of Training Cycles")
    
    view = View(Item('V_ds'),
                Item('I_ds_limit'),
                Item('V_high'),
                Item('V_low'),
                Item('I_g_limit'),
                Item('step_size'),
                Item('delay'),
                Item('cycles'),
                buttons = [OKButton, CancelButton])
    
        
setting1 = Settings()
#setting1.configure_traits()


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

class TrainingThread(Thread):
    def run(self):
        # Instrument Configuration
        # Channel A for Gate Voltage, Channel B for Source-Drain Voltage
    
        longbox.selectVoltageSourceFuncion(0)
        longbox.selectVoltageSourceFuncion(1)
    
        longbox.setVoltageSourceRange(0)
        longbox.setVoltageSourceLevel(0, 0)
        longbox.setVoltageSourceRange(1)
        longbox.setVoltageSourceLevel(1, setting1.V_ds)
        
        longbox.setCurrentLimit(0, float(setting1.I_g_limit)/10**9)
        longbox.setCurrentRange(0, float(setting1.I_g_limit)/10**9)
        longbox.setCurrentLimit(1, float(setting1.I_ds_limit)/10**9)
        longbox.setCurrentRange(1, float(setting1.I_ds_limit)/10**9)
        
        longbox.displayCurrentMeasurement(0)
        longbox.displayCurrentMeasurement(1)
    
        # Calculate Gate Voltage Sequence
        gateVoltageSequence = np.array([])
        gateVoltageCycle = np.array([])
        # *1000 because step size is in mV
        # from 0 to V_high
        steps = 1 + 1000 * (setting1.V_high - 0) / setting1.step_size
        gateVoltageCycle = np.append(gateVoltageCycle, np.linspace(0, setting1.V_high, steps))
        # from V_high to V_low
        steps = 1 + 1000 * (setting1.V_high - setting1.V_low) / setting1.step_size
        gateVoltageCycle = np.append(gateVoltageCycle, np.linspace(setting1.V_high, setting1.V_low, steps)) 
        # from V_low to 0
        steps = 1 + 1000 * (0 - setting1.V_low) / setting1.step_size
        gateVoltageCycle = np.append(gateVoltageCycle, np.linspace(setting1.V_low, 0, steps))
        for i in range(setting1.cycles):
            gateVoltageSequence = np.append(gateVoltageSequence, gateVoltageCycle)
            
        # Measurement Stage
        new_index = np.array([])
        new_data1 = np.array([])
        new_data2 = np.array([])
        new_data3 = np.array([])
        
        longbox.turnOnOutput(0)
        longbox.turnOnOutput(1)
        
        for j in range(gateVoltageSequence.size):
            if not self.wants_abort:                
                longbox.setVoltageSourceLevel(0, gateVoltageSequence[j])
                time.sleep(setting1.delay)
                        
                new_index = np.array(range(j+1))
                new_data1 = gateVoltageSequence[:(j+1)]
                new_data2 = np.append(new_data2, 10**9 * longbox.readCurrent(0))
                new_data3 = np.append(new_data3, 10**9 * longbox.readCurrent(1))
                

                self.viewer1.update_display(new_index, new_data1)
                self.viewer2.update_display(new_index, new_data2)
                self.viewer3.update_display(new_index, new_data3)
                
            else:
                print "Abort Training!"
                return
        #print new_data1, new_data2, new_data3        
        longbox.turnOffOutput(0)
        longbox.turnOffOutput(1)
                                
                                                
class Controller(HasTraits):

    # A reference to the plot viewer object
    viewer1 = Instance(Viewer)
    viewer2 = Instance(Viewer)
    viewer3 = Instance(Viewer)
    
    
    # Start and Stop Button
    btnSetting = Button("Training Settings")
    btnStart = Button("Start/Stop Training")
    btnSave = Button("Save Data")
    
    file_name = String()
    
    # TrainingThread
    training_thread = Instance(TrainingThread)
    
    def _btnSetting_fired(self):
        setting1.configure_traits()
    
    def _btnStart_fired(self):
        print "Start!"
        if self.training_thread and self.training_thread.isAlive():
            self.training_thread.wants_abort = True
        else:
            self.training_thread = TrainingThread()
            self.training_thread.wants_abort = False
            self.training_thread.viewer1 = self.viewer1
            self.training_thread.viewer2 = self.viewer2
            self.training_thread.viewer3 = self.viewer3
            self.training_thread.start()
    
    def _btnSave_fired(self):
        np.savetxt(self.file_name+"_index.txt", self.viewer1.dataset.get_data('x'))
        np.savetxt(self.file_name+"_gate_voltage_V.txt", self.viewer1.dataset.get_data('y'))
        np.savetxt(self.file_name+"_leakage_current_nA.txt", self.viewer2.dataset.get_data('y'))
        np.savetxt(self.file_name+"_source_drain_current_nA.txt", self.viewer3.dataset.get_data('y'))
        f = open(self.file_name+"_settings.txt", 'w')
        f.write("Source-Drain Voltage (V): %f \n" %setting1.V_ds)
        f.write("Source-Drain Current Limit (nA): %f \n" %setting1.I_ds_limit)
        f.write("High-end Gate Voltage (V): %f \n" %setting1.V_high)
        f.write("Low-end Gate Voltage (V): %f \n" %setting1.V_low)
        f.write("Leakage/Gate Current Limit (nA): %f \n" %setting1.I_g_limit)
        f.write("Ramp Step Size (mV): %f \n" %setting1.step_size)
        f.write("Delay Time (s): %f \n" %setting1.delay)
        f.write("Number of Training Cycles: %d \n" %setting1.cycles)
        f.close()
        
        
    view = View(
                Item('btnSetting', show_label = False),
                Item('btnStart', show_label = False),
                Item('file_name', width = 300),
                Item('btnSave', show_label = False)
                
               )
    
    
            

class Demo(HasTraits):
    viewer1 = Instance(Viewer, (), label = "  Gate Voltage (V)",)
    viewer2 = Instance(Viewer, (), label = "  Leakage Current (nA)",)
    viewer3 = Instance(Viewer, (), label = "  Source-Drain Current (nA)",)
    controller = Instance(Controller)
    
    def _controller_default(self):
        return Controller(viewer1=self.viewer1, viewer2=self.viewer2, viewer3=self.viewer3)
    
    view = View(
                Item('viewer1', style='custom', show_label=True),
                Item('viewer2', style='custom', show_label=True),
                Item('viewer3', style='custom', show_label=True),                
                Item('controller', style='custom', show_label=False),                
                resizable=True)


#mainWindow = Demo()
#mainWindow.configure_traits()



        
