#Cryomagnetics4G Superconducting Magnet Controller

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

import cryomagnetics4g

buzzy = cryomagnetics4g.Cryomagnetics4G(6)


class RecordingThread(Thread):
    def run(self):
                         
        j = 0
        while (not self.wants_abort):
            now = time.time()
            
            self.parent.sweep_mode = buzzy.querySweepMode()
            self.parent.output_current = buzzy.queryOutputCurrent()
            self.parent.output_voltage = buzzy.queryOutputVoltage()
            self.parent.pshtr_on = buzzy.queryPersistentSwitchHeater()
            self.parent.magnet_current = buzzy.queryMagnetCurrent()
            self.parent.magnet_voltage = buzzy.queryMagnetVoltage()            

            j+=1
            
            #For Test
            #print "j=", j
            
            elapsed = time.time() - now
            
            if (self.interval - elapsed > 0):
                time.sleep(self.interval - elapsed)
            else:
                print "Record Time Interval Too Small!"
                self.wants_abort = True
                
        print "Abort Recording!"

        return


class MainWindow(HasTraits):
    safety_notes = String(" !!! Caution: Magnet temperature should be always lower than 4.2K\n  Ramp Rate should not exceed 0.3475T/min for 0~4.82T; 0.1158T/min for 4.82T~9T")
    
    sweep_mode = String(buzzy.querySweepMode(), label = "Sweep Mode:")
    output_current = Float(buzzy.queryOutputCurrent(), label = "Output Current (T):")
    output_voltage = Float(buzzy.queryOutputVoltage(), label = "Output Voltage (V):")
    
    
    pshtr_on = Bool(buzzy.queryPersistentSwitchHeater(), label = "Persistent Switch Heater ON")
    magnet_current = Float(buzzy.queryMagnetCurrent(), label = "Magnet Current (T):")
    magnet_voltage = Float(buzzy.queryMagnetVoltage(), label = "Magnet Voltage (V):")
    
    btnToggleHeater = Button("Toggle Persistent Switch Heater")
    
    def _btnToggleHeater_fired(self):
        self.pshtr_on = buzzy.queryPersistentSwitchHeater()
        if self.pshtr_on:
            buzzy.setPersistentSwitchHeater("OFF")
        else:
            buzzy.setPersistentSwitchHeater("ON")
        self.pshtr_on = buzzy.queryPersistentSwitchHeater()
            
    btnSweepUp = Button("Sweep UP "+u"\u25B2")
    
    def _btnSweepUp_fired(self):
        buzzy.setSweepMode("UP")

    btnSweepDown = Button("Sweep DOWN "+u"\u25BC")
    
    def _btnSweepDown_fired(self):
        buzzy.setSweepMode("DOWN")

    btnPause = Button("PAUSE")
    
    def _btnPause_fired(self):
        buzzy.setSweepMode("PAUSE")

    btnZero = Button("ZERO")
    
    def _btnZero_fired(self):
        buzzy.setSweepMode("ZERO")

    upper_limit = Float(buzzy.queryUpperLimit(), label = "Upper Limit (T):")
    lower_limit = Float(buzzy.queryLowerLimit(), label = "Lower Limit (T):")
    voltage_limit = Float(buzzy.queryVoltageLimit(), label = "Voltage Limit (V):")
    upper_limit_toset = Float(0.1, label = "Set Upper Limit (T):")
    lower_limit_toset = Float(-0.1, label = "Set Lower Limit (T):")
    
    btnSetUpperLimit = Button("Set Upper Limit")
    btnSetLowerLimit = Button("Set Lower Limit")    
    
    def _btnSetUpperLimit_fired(self):
        buzzy.setUpperLimit(self.upper_limit_toset)
        self.upper_limit = buzzy.queryUpperLimit()
    def _btnSetLowerLimit_fired(self):
        buzzy.setLowerLimit(self.lower_limit_toset)
        self.lower_limit = buzzy.queryLowerLimit()    
    
    rate0 = Float(buzzy.queryRateLimit(0), label = "[0~4.82T] Ramp Rate (T/min):")
    rate1 = Float(buzzy.queryRateLimit(1), label = "[4.82T~9T] Ramp Rate (T/min):")
    rate0_toset = Float(0.1, label = "Set [0~4.82T] Ramp Rate (T/min):")
    rate1_toset = Float(0.05, label = "Set [4.82T~9T] Ramp Rate (T/min):")
    
    btnSetRate0 = Button("Set [0~4.82T] Ramp Rate")
    btnSetRate1 = Button("Set [4.82T~9T] Ramp Rate")
    
    def _btnSetRate0_fired(self):
        buzzy.setRate(0, self.rate0_toset)
        self.rate0 = self.rate0_toset
    def _btnSetRate1_fired(self):
        buzzy.setRate(1, self.rate1_toset)
        self.rate1 = self.rate1_toset
        
    # Select Recording Time Interval
    interval = Enum(1, 3, 10, 30, 60, label="Update Interval (s)")
    
    # Start and Stop Button

    btnStart = Button("Start/Stop Update")
    
    # RecordingThread
    recording_thread = Instance(RecordingThread)
    
    
    def _btnStart_fired(self):
        if self.recording_thread and self.recording_thread.isAlive():
            self.recording_thread.wants_abort = True
        else:
            print "Start Recording!"
            self.recording_thread = RecordingThread()
            self.recording_thread.wants_abort = False
            self.recording_thread.interval = self.interval
            self.recording_thread.parent = self
            self.recording_thread.start()
    
            
    view = View(
                Item("safety_notes", style = "readonly", show_label = False),
                Group(
                      Group(Item("sweep_mode", style = "readonly"),
                            Item("output_current", style = "readonly"),
                            Item("output_voltage", style = "readonly"),
                            show_border = True,
                            orientation = 'vertical',
                            label = 'Output',
                            ),
                      Group(Item("pshtr_on", style = "readonly"),
                            Item("magnet_current", style = "readonly"),
                            Item("magnet_voltage", style = "readonly"),
                            show_border = True,
                            orientation = 'vertical',
                            label = 'Magnet',
                            ),
                      show_border = True,
                      orientation = 'horizontal',
                      ),
                Group(
                      Group(
                            Item("upper_limit", style = "readonly"),
                            Item("lower_limit", style = "readonly"),
                            Item("voltage_limit", style = "readonly"),
                            show_border = True,
                            orientation = 'horizontal',
                      ),  
                      Group(Item("upper_limit_toset", style = "simple"),
                            Item("btnSetUpperLimit", style = "custom", show_label = False),
                            Item("lower_limit_toset", style = "simple"),
                            Item("btnSetLowerLimit", style = "custom", show_label = False),
                            show_border = True,
                            orientation = 'horizontal',
                            ),                           
                      show_border = True,
                      orientation = 'vertical',
                      label = 'Limits'
                      ), 
                Group(
                      Item("btnToggleHeater", style = "custom", show_label = False),
                      Item("btnSweepUp", style = "custom", show_label = False),
                      Item("btnSweepDown", style = "custom", show_label = False),
                      Item("btnPause", style = "custom", show_label = False),
                      Item("btnZero", style = "custom", show_label = False),
                      show_border = True,
                      orientation = 'horizontal',
                      label = 'Control',
                      ),                      
                Group(
                      Group(
                            Item("rate0", style = "readonly"),
                            Item("rate1", style = "readonly"),
                            show_border = True,
                            orientation = 'horizontal',
                      ),  
                      Group(Item("rate0_toset", style = "simple"),
                            Item("btnSetRate0", style = "custom", show_label = False),
                            Item("rate1_toset", style = "simple"),
                            Item("btnSetRate1", style = "custom", show_label = False),
                            show_border = True,
                            orientation = 'horizontal',
                            ),                           
                      show_border = True,
                      orientation = 'vertical',
                      label = "Rates"
                      ),                      
                Group(
                      Item('interval', show_label = True),
                      Item('btnStart', show_label = False),
                      show_border = True,
                      orientation = 'horizontal',
                      label = 'Update Status',
                      ),                                          
                title = "Cryomagnetics Model 4G Superconducting Magnet Controller "      
                )
    
    
    