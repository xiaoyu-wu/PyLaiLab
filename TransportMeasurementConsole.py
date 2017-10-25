# Controller for Keithley 2634B
# Tested on AttoDry system in Feb. 2016

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

import k2634b

# Initialization of K2634B
longbox = k2634b.K2634B(26)
#longbox.reset()

#longbox.selectVoltageSourceFuncion(0)
#longbox.selectVoltageSourceFuncion(1)
    
#longbox.setVoltageSourceRange(0)
#longbox.setVoltageSourceLevel(0, 0)

#longbox.setVoltageSourceRange(1)
#longbox.setVoltageSourceLevel(1, 0)

#longbox.displayCurrentMeasurement(0)
#longbox.displayCurrentMeasurement(1)

# Ion Gel Training
import IonGelDeviceTraining

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

class Settings(HasTraits):
    V_source = Float(0.01, label = "Source Voltage (V)")
    I_limit = Float(10, label = "Current Limit (nA)")
    step_size = Float(1, label = "Ramp Step Size (mV)")
    delay = Float(1, label = "Delay Time (s)")    
    
    view = View(
                Group(
                      Group(
                            Item('V_source'),
                            Item('I_limit'),
                            orientation = 'horizontal'
                            ),
                      Group(
                            Item('step_size'),
                            Item('delay'),
                            orientation = 'horizontal'
                            ),
                      orientation = 'vertical',
                      show_border = True,
                      ),
                 resizable = True,
                 )

class RecordingThread(Thread):
    def run(self):
        # Instrument Configuration Kept Unchanged
    
        # Measurement Stage
        new_time = np.array([])
        new_data_a1 = np.array([])
        new_data_a2 = np.array([])
        new_data_b1 = np.array([])
        new_data_b2 = np.array([])
                          
        j = 0
        while (not self.wants_abort):
            now = time.time()
            
            new_index = range(j+1)
            new_time = np.array([ i * self.interval for i in new_index ])
            
            ia, va = longbox.readCurrentAndVoltage(0)   
            new_data_a1 = np.append(new_data_a1, 10**9 * ia)
            new_data_a2 = np.append(new_data_a2, va)
            ib, vb = longbox.readCurrentAndVoltage(1) 
            new_data_b1 = np.append(new_data_b1, 10**9 * ib)
            new_data_b2 = np.append(new_data_b2, vb)
            
            self.viewer_a1.update_display(new_time, new_data_a1)
            self.viewer_a2.update_display(new_time, new_data_a2)
            self.viewer_b1.update_display(new_time, new_data_b1)
            self.viewer_b2.update_display(new_time, new_data_b2)
            self.transport_plots.viewer_ia_va.update_display(new_data_a2, new_data_a1)
            self.transport_plots.viewer_ib_vb.update_display(new_data_b2, new_data_b1)
            self.transport_plots.viewer_ia_vb.update_display(new_data_b2, new_data_a1)           
            
            j+=1
            
            elapsed = time.time() - now
            
            if (self.interval - elapsed > 0):
                time.sleep(self.interval - elapsed)
            else:
                print "Record Time Interval Too Small!"
                self.wants_abort = True
                
        print "Abort Recording!"

        return


class ApplySettingThread(Thread):
    def run(self):
        longbox.setCurrentLimit(self.channel_num, float(self.setting.I_limit)/10**9)
        longbox.setCurrentRange(self.channel_num, float(self.setting.I_limit)/10**9)
        level_now = longbox.readVoltageLevel(self.channel_num)
        level_set = self.setting.V_source
        if (level_set >= level_now):
            print "Ramp up!"
            steps = 1 + float(level_set - level_now) / (float(self.setting.step_size) / 1000)
        else:
            print "Ramp down"
            steps = 1 + float(level_now - level_set) / (float(self.setting.step_size) / 1000)
        steps = int(steps)
        level_list = np.linspace(level_now, level_set, steps)
        j = 1            
        while (not self.wants_abort):
            now = time.time()
            longbox.setVoltageSourceLevel(self.channel_num, level_list[j])
            elapsed = time.time() - now
            if (self.setting.delay - elapsed > 0):
                time.sleep(self.setting.delay - elapsed)
            else:
                print "Delay Time Too Small!"
                self.wants_abort = True
            j+=1
            if j==int(steps):
                self.wants_abort = True 
        return


class Controller(HasTraits):

    # A reference to the plot viewer object
    viewer_a1 = Instance(Viewer)
    viewer_a2 = Instance(Viewer)
    viewer_b1 = Instance(Viewer)
    viewer_b2 = Instance(Viewer)
    
    # Reference to Settings
    setting_a = Instance(Settings)
    setting_b = Instance(Settings)
    
    # Output ON/OFF
    output_on_a = Bool(label = "Channel A Output ON")
    output_on_b = Bool(label = "Channel B Output ON")
    # Set output Button
    btnSetOutput = Button("Set Output")
    
    def _btnSetOutput_fired(self):
        if self.output_on_a:
            longbox.turnOnOutput(0)
        else:
            longbox.turnOffOutput(0)
        if self.output_on_b:
            longbox.turnOnOutput(1)
        else:
            longbox.turnOffOutput(1)

    # Apply Setting A & B Button
    btnApplySettingA = Button("Apply Channel A Settings")
    btnApplySettingB = Button("Apply Channel B Settings")
    
    # Apply Setting Thread
    apply_setting_thread = Instance(ApplySettingThread)
    apply_setting_thread2 = Instance(ApplySettingThread)
    def _btnApplySettingA_fired(self):
        if self.apply_setting_thread and self.apply_setting_thread.isAlive():
            self.apply_setting_thread.wants_abort = True
        else:
            print "Start Apply Setting!"
            self.apply_setting_thread = ApplySettingThread()
            self.apply_setting_thread.wants_abort = False
            self.apply_setting_thread.channel_num = 0
            self.apply_setting_thread.setting = self.setting_a
            self.apply_setting_thread.start()    

    def _btnApplySettingB_fired(self):
        if self.apply_setting_thread2 and self.apply_setting_thread2.isAlive():
            self.apply_setting_thread2.wants_abort = True
        else:
            print "Start Apply Setting!"
            self.apply_setting_thread2 = ApplySettingThread()
            self.apply_setting_thread2.wants_abort = False
            self.apply_setting_thread2.channel_num = 1
            self.apply_setting_thread2.setting = self.setting_b
            self.apply_setting_thread2.start()  
                                    
    # Select Recording Time Interval
    interval = Enum(1, 3, 10, 30, 60, label="Record Interval (s)")
    
    # Start and Stop Button

    btnStart = Button("Start/Stop Recording")
    btnSave = Button("Save Data")
    
    file_name = String()
    
    # RecordingThread
    recording_thread = Instance(RecordingThread)
    
    
    def _btnStart_fired(self):
        if self.recording_thread and self.recording_thread.isAlive():
            self.recording_thread.wants_abort = True
        else:
            print "Start Recording!"
            self.recording_thread = RecordingThread()
            self.recording_thread.wants_abort = False
            self.recording_thread.viewer_a1 = self.viewer_a1
            self.recording_thread.viewer_a2 = self.viewer_a2
            self.recording_thread.viewer_b1 = self.viewer_b1
            self.recording_thread.viewer_b2 = self.viewer_b2
            self.recording_thread.interval = self.interval
            self.recording_thread.transport_plots = self.transport_plots
            self.recording_thread.start()
    
    def _btnSave_fired(self):
        np.savetxt(self.file_name+"_time.txt", self.viewer_a1.dataset.get_data('x'))
        np.savetxt(self.file_name+"_A_current_nA.txt", self.viewer_a1.dataset.get_data('y'))
        np.savetxt(self.file_name+"_A_voltage_V.txt", self.viewer_a2.dataset.get_data('y'))
        np.savetxt(self.file_name+"_B_current_nA.txt", self.viewer_b1.dataset.get_data('y'))
        np.savetxt(self.file_name+"_B_voltage_V.txt", self.viewer_b2.dataset.get_data('y'))
        f = open(self.file_name+"_log.txt", 'w')
        f.write(time.strftime("%d %b %Y %H:%M:%S \n", time.localtime()))
        f.write("Channel A Voltage (V): %f \n" %self.setting_a.V_source)
        f.write("Channel A Current Limit (nA): %f \n" %self.setting_a.I_limit)
        f.write("Channel A Ramp Step Size (mV): %f \n" %self.setting_a.step_size)
        f.write("Channel A Delay Time (s): %f \n" %self.setting_a.delay)
        f.write("Channel B Voltage (V): %f \n" %self.setting_b.V_source)
        f.write("Channel B Current Limit (nA): %f \n" %self.setting_b.I_limit)
        f.write("Channel B Ramp Step Size (mV): %f \n" %self.setting_b.step_size)
        f.write("Channel B Delay Time (s): %f \n" %self.setting_b.delay)        
        f.close()
        
        
    view = View(
                Group(
                      Group(
                            Group(
                                  Item('output_on_a'),
                                  Item('output_on_b'),
                                  Item('btnSetOutput', show_label = False),
                                  show_border = False,
                                  orientation = 'horizontal',
                                  ),
                            Group(
                                  Item('btnApplySettingA', show_label = False),
                                  Item('btnApplySettingB', show_label = False),
                                  show_border = False,
                                  orientation = 'horizontal',                                
                                  ),
                            label = 'Basic',
                            orientation = 'vertical',
                            show_border = True
                            ),
                      Group(
                            Item('interval', show_label = True),
                            Item('btnStart', show_label = False),
                            Item('file_name', width = 50),
                            Item('btnSave', show_label = False),
                            show_border = True,
                            orientation = 'horizontal',
                            label = 'Record',
                            ),
                      )          
               )


class TransportPlots(HasTraits):
    viewer_ia_va = Instance(Viewer, (), label = "Channel A Current vs Voltage")
    viewer_ib_vb = Instance(Viewer, (), label = "Channel B Current vs Voltage")
    viewer_ia_vb = Instance(Viewer, (), label = "Channel A Current vs Channel B Voltage")
    view = View(Item('viewer_ia_va', style='custom', show_label=True),
                Item('viewer_ib_vb', style='custom', show_label=True),
                Item('viewer_ia_vb', style='custom', show_label=True),
                title = "Transport Plots",
                resizable = True
                )
    

class MainWindow(HasTraits):
    viewer_a1 = Instance(Viewer, (), label = "Channel A Current (nA)",)
    viewer_a2 = Instance(Viewer, (), label = "Channel A Voltage (V)",)
    
    viewer_b1 = Instance(Viewer, (), label = "Channel B Current (nA)",)
    viewer_b2 = Instance(Viewer, (), label = "Channel B Voltage (V)",)
    
    setting_a = Instance(Settings)
    setting_b = Instance(Settings)
    
    def _setting_a_default(self):
        return Settings()
    def _setting_b_default(self):
        return Settings()
    
    controller = Instance(Controller)
    
    def _controller_default(self):
        return Controller(viewer_a1=self.viewer_a1, viewer_a2=self.viewer_a2,
                          viewer_b1=self.viewer_b1, viewer_b2=self.viewer_b2,
                          setting_a=self.setting_a, setting_b=self.setting_b,
                          transport_plots=self.transport_plots)
            

    # Transport Plots
    transport_plots = Instance(TransportPlots)
    def _transport_plots_default(self):
        return TransportPlots()
    
    # Show Transport Plots
    btnShowTransportPlots = Button("Show Transport Plots")
    def _btnShowTransportPlots_fired(self):
        self.transport_plots.configure_traits()
        
    # Show Ion Gel Device Training Interface
    IGDT = Instance(IonGelDeviceTraining.Demo)
    def _IGDT_default(self):
        return IonGelDeviceTraining.Demo()
    btnShowIGDT = Button("Ion Gel Device Training")
    def _btnShowIGDT_fired(self):
        self.IGDT.configure_traits()
        
    
    view = View(
                Group(
                      Group(
                            Group(
                                  Item('viewer_a1', style='custom', show_label=True),
                                  Item('viewer_a2', style='custom', show_label=True),
                                  orientation = 'vertical'
                                  ),
                            Group(
                                  Item('viewer_b1', style='custom', show_label=True),
                                  Item('viewer_b2', style='custom', show_label=True),
                                  orientation = 'vertical'                        
                                  ),
                            orientation = 'horizontal',
                      ),
                      Group(
                            Item('setting_a', style="custom", label = "Setting A"),
                            Item('setting_b', style="custom", label = "Setting B"),
                            orientation = 'horizontal',
                            show_labels = True,                            
                            ),
                      orientation = 'vertical',
                      ),
                      Item('controller', style="custom"),
                      Item('btnShowTransportPlots', style="custom", show_label=False),
                      Item('btnShowIGDT', style="custom", show_label=False),
                      resizable = True,
                      title = "Keithley2634B Control Console"
                )
             
# main = MainWindow()
# main.configure_traits()