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

# Print into a Log File
import sys
orig_stdout = sys.stdout
f = file(time.strftime("%Y%m%d_%H%M%S", time.localtime())+' log of attodry console.txt', 'w')
sys.stdout = f

def LogTime():
    print "*"*20
    print time.strftime("%Y %m %d %H:%M:%S", time.localtime())

LogTime()



# Instrument Packages

import k2634b
import attodry1100
import cryomagnetics4g
import srs830


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

# Initialization of AttoDry1100
coolboy = attodry1100.AttoDry1100(3)

# Define Cryomagnetics 4G
buzzy = cryomagnetics4g.Cryomagnetics4G(6)

# Define SRS830 Lock-in
grey = srs830.SRS830(8)

# K2634B console
import TransportMeasurementConsole as TMC

# Cryomagnetics 4G console
import MagnetControllerConsole as MCC

class Data(HasTraits):
    name = String("")
    info = Instance(np.array([]))
    
    

class Status(HasTraits):
    name = String("")
    info = Float(0)
    view = View(Group(Item('name', style = 'readonly', show_label = False), 
                      Item('info', style = 'readonly', show_label = False),
                      orientation = 'horizontal',
                      show_border = True,))

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

#class Viewer2(HasTraits):
#    # Log Scale
#
#    dataset = Instance(ArrayPlotData)
#    plot = Instance(Plot)
#
#    def _dataset_default(self):
#        x = []
#        y = []
#        plotdata = ArrayPlotData(x=x, y=y)
#        return plotdata
#
#    def _plot_default(self):
#        plot = Plot(self.dataset, border_visible=True)
#        plot.plot(('x', 'y'), color="blue", value_scale = 'log')
#        return plot
#
#    def update_display(self, x, y):
#        self.dataset.set_data('x', x)
#        self.dataset.set_data('y', y)
#
#    traits_view = View(
#        Item('plot', editor=ComponentEditor(), show_label=False,
#             width = 300, height = 200, resizable = True)
#    )

class Viewer2(Viewer):
    # Log Scale

    def _plot_default(self):
        plot = Plot(self.dataset, border_visible=True)
        plot.plot(('x', 'y'), color="blue", value_scale = 'log')
        return plot


class UpdateThread(Thread):

    def run(self):
        #Initialize Parameter Histroy Lists
        self.time_data.info = np.array([])
        self.t_user_data.info = np.array([])
        self.t_sample_data.info = np.array([])
        self.t_magnet_data.info = np.array([])
        self.t_vti_data.info = np.array([])
        self.mag_field_setpoint_data.info = np.array([])
        self.mag_field_data.info = np.array([])
        self.pressure_data.info = np.array([])
        self.sample_heater_power_data.info = np.array([])
                                            
        j = 0
        while (not self.wants_abort):
            now = time.time()
            
            index_list = range(j+1)
            self.time_data.info = np.array([ i * self.interval for i in index_list ])
            
            self.t_user_data.info = np.append(self.t_user_data.info, coolboy.getUserTemperature())
            self.viewer_t_user.update_display(self.time_data.info, self.t_user_data.info)
            self.parent.t_user = self.t_user_data.info[-1]
            
            self.t_sample_data.info = np.append(self.t_sample_data.info, coolboy.getSampleTemperature())
            self.viewer_t_sample.update_display(self.time_data.info, self.t_sample_data.info)
            self.parent.t_sample = self.t_sample_data.info[-1]         

            self.t_magnet_data.info = np.append(self.t_magnet_data.info, coolboy.getMagnetTemperature())
            self.viewer_t_magnet.update_display(self.time_data.info, self.t_magnet_data.info)
            self.parent.t_magnet = self.t_magnet_data.info[-1] 
            
            self.t_vti_data.info = np.append(self.t_vti_data.info, coolboy.getVtiTemperature())
            self.viewer_t_vti.update_display(self.time_data.info, self.t_vti_data.info)
            self.parent.t_vti = self.t_vti_data.info[-1]                                     

            self.mag_field_setpoint_data.info = np.append(self.mag_field_setpoint_data.info, coolboy.getMagneticFieldSetPoint())
            self.viewer_mag_field_setpoint.update_display(self.time_data.info, self.mag_field_setpoint_data.info)
            self.parent.mag_field_setpoint = self.mag_field_setpoint_data.info[-1]
              
            self.mag_field_data.info = np.append(self.mag_field_data.info, coolboy.getMagneticField())
            self.viewer_mag_field.update_display(self.time_data.info, self.mag_field_data.info)
            self.parent.mag_field = self.mag_field_data.info[-1]
            
            self.pressure_data.info = np.append(self.pressure_data.info, coolboy.getPressure())
            self.viewer_pressure.update_display(self.time_data.info, self.pressure_data.info)
            self.parent.pressure = self.pressure_data.info[-1]
            
            self.sample_heater_power_data.info = np.append(self.sample_heater_power_data.info, coolboy.getSampleHeaterPower())
            self.viewer_sample_heater_power.update_display(self.time_data.info, self.sample_heater_power_data.info)
            self.parent.sample_heater_power = self.sample_heater_power_data.info[-1]                                                                                                                                                                                                            
            
            self.parent.vti_heater_power = coolboy.getVtiHeaterPower()
            self.parent.turbopump_freq = coolboy.getTurbopumpFrequency()
            self.parent.p_gain = coolboy.getProportionalGain()
            self.parent.i_gain = coolboy.getIntegralGain()
            self.parent.d_gain = coolboy.getDerivativeGain()
            
            self.parent.inner_volume_valve_status = bool(coolboy.getInnerVolumeValve())
            self.parent.outer_volume_valve_status = bool(coolboy.getOuterVolumeValve())
            self.parent.pump_valve_status = bool(coolboy.getPumpValve())
            self.parent.helium_valve_status = bool(coolboy.getHeliumValve())
            self.parent.pump_status = bool(coolboy.isPumping())
            # Something wrong with the function getTurboFrequency, it returns a number of 1.68156*10**(-42) when freq = 1200 Hz
            self.parent.turbo_freq = float(coolboy.getTurbopumpFrequency())*1200/1.68156*10**42
            
            j+=1
            
            elapsed = time.time() - now
            
            if (self.interval - elapsed > 0):
                time.sleep(self.interval - elapsed)
            else:
                LogTime()
                print "Update Time Interval Too Small!"
                self.wants_abort = True
                
        LogTime()
        print "Abort Updating!"

        return

class RampTempThread(Thread):
    def run(self):
        
        temp_now = coolboy.getUserTemperature()
        temp_set = self.temp_set
        # Convert from K/min to K/10s
        ramp_rate = self.ramp_rate /60.0 * 10
        if (temp_set >= temp_now):
            print "Ramp up!"
            steps = 1 + float(temp_set - temp_now) / ramp_rate
        else:
            print "Ramp down"
            steps = 1 + float(temp_now - temp_set) / ramp_rate
        steps = int(steps)
        temp_list = np.linspace(temp_now, temp_set, steps)
        j = 1            
        while (not self.wants_abort):
            now = time.time()
            coolboy.setUserTemperature(temp_list[j])
            elapsed = time.time() - now
            if (10 - elapsed > 0):
                time.sleep(10 - elapsed)
            else:
                print "Delay Time Too Small!"
                self.wants_abort = True
            j+=1
            if j==int(steps):
                self.wants_abort = True 
        return


class DepUpdateThread(Thread):
    
    def run(self):
        #Initialize Parameter Histroy Lists
        self.time_data.info = np.array([])
        self.temp_data.info = np.array([])
        self.mag_data.info = np.array([])
        self.a_current_data.info = np.array([])
                                                 
        j = 0
        while (not self.wants_abort):
            now = time.time()
            
            index_list = range(j+1)
            self.time_data.info = np.array([ i * self.interval for i in index_list ])
            
            self.temp_data.info = np.append(self.temp_data.info, coolboy.getSampleTemperature())
            self.mag_data.info = np.append(self.mag_data.info, self.buzzy.i_mag)
            # For 2-terminal measurements:
            #self.a_current_data.info = np.append(self.a_current_data.info, 10**9 * longbox.readCurrent(0))
            # For 4-terminal measurements using SRS830:
            grey.outp(3)
            self.a_current_data.info = np.append(self.a_current_data.info, grey.R)
            
            self.viewer_temp_dep_a.update_display(self.temp_data.info, self.a_current_data.info)
            self.viewer_mag_dep_a.update_display(self.mag_data.info, self.a_current_data.info)
                    
            j+=1
            
            elapsed = time.time() - now
            
            if (self.interval - elapsed > 0):
                time.sleep(self.interval - elapsed)
            else:
                LogTime()
                print "Dependence Update Time Interval Too Small!"
                self.wants_abort = True
                
        LogTime()
        print "Abort Dependence Updating!"

        return


class TempMagDependenceWindow(HasTraits):
    viewer_temp_dep_a = Instance(Viewer, (), label = "Ch. A Current (nA) vs Temp(K)",) 

    viewer_mag_dep_a = Instance(Viewer, (), label = "Ch. A Current (nA) vs Mag. Field (T)",)
    
    time_data = Data()
    time_data.name = "Time (s)"
    time_data.info = np.array([])

    temp_data = Data()
    temp_data.name = "Sample Temperature (K)"
    temp_data.info = np.array([])

    mag_data = Data()
    mag_data.name = "Magnetic Field (T)"
    mag_data.info = np.array([])
            
    a_current_data = Data()
    a_current_data.name = "Ch. A Current (nA)"
    a_current_data.info = np.array([])
     
      
    # Select Update Time Interval
    interval = Enum(1, 3, 10, 30, 60, label="Update Interval (s)")

    # UpdateThread
    dep_update_thread = Instance(DepUpdateThread)
    
    btnStartUpdate = Button("Start/Stop Dependence Record")

    all_data = [time_data, temp_data, mag_data, a_current_data]
        
    def _btnStartUpdate_fired(self):
        if self.dep_update_thread and self.dep_update_thread.isAlive():
            self.dep_update_thread.wants_abort = True
        else:
            LogTime()
            print "Start Dependence Update!"
            
            self.dep_update_thread = DepUpdateThread()
            self.dep_update_thread.wants_abort = False
            
            self.dep_update_thread.viewer_temp_dep_a = self.viewer_temp_dep_a
            self.dep_update_thread.viewer_mag_dep_a = self.viewer_mag_dep_a

            self.dep_update_thread.interval = self.interval
            self.dep_update_thread.time_data = self.time_data
            self.dep_update_thread.temp_data = self.temp_data
            self.dep_update_thread.mag_data = self.mag_data
            self.dep_update_thread.a_current_data = self.a_current_data
            self.dep_update_thread.buzzy = self.buzzy
            
            # Not Giving thread access to all the parameters in its parent window
            # self.dep_update_thread.parent = self
            
            self.dep_update_thread.start()    
      
    btnSave = Button("Save Data")
    file_name = String()
    
    def _btnSave_fired(self):
        
        for data in self.all_data:
            np.savetxt(self.file_name+"_synchronized_"+data.name+".txt", data.info)
            
        LogTime()
        print "Dependence Data Saved."      

    view = View(Item('viewer_temp_dep_a', style='custom', show_label=True),
                Item('viewer_mag_dep_a', style='custom', show_label=True),
                Group(
                      Item('interval', show_label = True),
                      Item('btnStartUpdate', show_label = False),
                      Item('file_name', width=50),
                      Item('btnSave', show_label = False),
                      orientation = "horizontal",
                      ),                
                resizable = True,
                title = "Temperature / Magnetic Field Dependence Console"
                ) 

class MainWindow(HasTraits):
    
    time_data = Data()
    time_data.name = "Time (s)"
    time_data.info = np.array([0])
    
    viewer_t_user = Instance(Viewer, (), label = "User Temp. (K) vs Time",) 
    t_user_data = Data()
    t_user_data.name = "User Temperature (K)"
    t_user_data.info = np.array([coolboy.getUserTemperature()])
    t_user = Float(t_user_data.info[-1], label = "User Temperature (K):")
        
    viewer_t_sample = Instance(Viewer, (), label = "Sample Temp. (K) vs Time",)    
    t_sample_data = Data()
    t_sample_data.name = "Sample Temperature (K)"                                
    t_sample_data.info = np.array([coolboy.getSampleTemperature()])
    t_sample = Float(t_sample_data.info[-1], label = "Sample Temperature (K):")
    
    viewer_t_magnet = Instance(Viewer, (), label = "Magnet Temp. (K) vs Time",)
    t_magnet_data = Data()
    t_magnet_data.name = "Magnet Temperature (K)"      
    t_magnet_data.info = np.array([coolboy.getMagnetTemperature()])
    t_magnet = Float(t_magnet_data.info[-1], label = "Magnet Temperature (K):")
    
    viewer_t_vti = Instance(Viewer, (), label = "VTI Temp. (K) vs Time",)
    t_vti_data = Data()
    t_vti_data.name = "VTI Temperature (K)"      
    t_vti_data.info = np.array([coolboy.getVtiTemperature()])
    t_vti = Float(t_vti_data.info[-1], label = "VTI Temperature (K):")    
    
    viewer_mag_field_setpoint = Instance(Viewer, (), label = "Magnetic Field Set Point (T) vs Time",)
    mag_field_setpoint_data = Data()
    mag_field_setpoint_data.name = "Magnetic Field Set Point (T)"     
    mag_field_setpoint_data.info = np.array([coolboy.getMagneticFieldSetPoint()])
    mag_field_setpoint = Float(mag_field_setpoint_data.info[-1], label = "Magnetic Field Set Point (T):")     
      
    viewer_mag_field = Instance(Viewer, (), label = "Magnetic Field (T) vs Time",)
    mag_field_data = Data()
    mag_field_data.name = "Magnetic Field (T)"    
    mag_field_data.info = np.array([coolboy.getMagneticField()])
    mag_field = Float(mag_field_data.info[-1], label = "Magnetic Field (T):")    

    viewer_pressure = Instance(Viewer2, (), label = "Pressure (mbar) vs Time",)
    pressure_data = Data()
    pressure_data.name = "Pressure (mbar)"     
    pressure_data.info = np.array([coolboy.getPressure()])
    pressure = Float(pressure_data.info[-1], label = "Pressure (mbar):")
    
    viewer_sample_heater_power = Instance(Viewer, (), label = "Sample Heater Power (W) vs Time",)
    sample_heater_power_data = Data()
    sample_heater_power_data.name = "Sample Heater Power (W)"    
    sample_heater_power_data.info = np.array([coolboy.getSampleHeaterPower()])
    sample_heater_power = Float(sample_heater_power_data.info[-1], label = "Sample Heater Power (W):")
    
    vti_heater_power = Float(coolboy.getVtiHeaterPower(), label = "  -- VTI Heater Power (W):")
    turbopump_freq = Float(coolboy.getTurbopumpFrequency(), label = "  -- Turbo Pump Frequency (Hz):")
    p_gain = Float(coolboy.getProportionalGain(), label = "  -- Proportional Gain:")
    i_gain = Float(coolboy.getIntegralGain(), label = "  -- Integral Gain:")
    d_gain = Float(coolboy.getDerivativeGain(), label = "  -- Derivative Gain:")

    all_data = [time_data, t_user_data, t_sample_data, t_magnet_data, t_vti_data, 
                mag_field_setpoint_data, mag_field_data, pressure_data, sample_heater_power_data]      
            
    error_message = String(coolboy.getAttodryErrorMessage(), label = "  -- Error Message:")
    btnLowerError = Button("Lower Error")
    def _btnLowerError_fired(self):
        LogTime()
        print "Error Lowered."
        coolboy.lowerError()
    
    action_message = String(coolboy.getActionMessage(), label = "  -- Action Message:")                                                
 
    inner_volume_valve_status = Bool(coolboy.getInnerVolumeValve(), label = "Inner Volume Valve Open:")    
    btnToggleInnerVolumeValve = Button("Toggle Inner Volume Valve")
    
    def _btnToggleInnerVolumeValve_fired(self):
        LogTime()
        coolboy.toggleInnerVolumeValve()
        time.sleep(1)
        
        if coolboy.getInnerVolumeValve():
            print "Inner Volume Valve is Open!"
            self.inner_volume_valve_status = True
        else:
            print "Inner Volume Valve is Closed!"
            self.inner_volume_valve_status = False            
        
    outer_volume_valve_status = Bool(coolboy.getOuterVolumeValve(), label = "Outer Volume Valve Open:")    
    btnToggleOuterVolumeValve = Button("Toggle Outer Volume Valve")
    
    def _btnToggleOuterVolumeValve_fired(self):
        LogTime()
        coolboy.toggleOuterVolumeValve()
        time.sleep(1)
        
        if coolboy.getOuterVolumeValve():
            print "Outer Volume Valve is Open!"
            self.outer_volume_valve_status = True
        else:
            print "Outer Volume Valve is Closed!"
            self.outer_volume_valve_status = False 
   
    pump_valve_status = Bool(coolboy.getPumpValve(), label = "Pump Valve Open:")    
    btnTogglePumpValve = Button("Toggle Pump Valve")
    
    def _btnTogglePumpValve_fired(self):
        LogTime()
        coolboy.togglePumpValve()
        time.sleep(1)
        
        if coolboy.getPumpValve():
            print "Pump Valve is Open!"
            self.pump_valve_status = True
        else:
            print "Pump Valve is Closed!"
            self.pump_valve_status = False 
            

    helium_valve_status = Bool(coolboy.getHeliumValve(), label = "Helium Valve Open:")    
    btnToggleHeliumValve = Button("Toggle Helium Valve")
    
    def _btnToggleHeliumValve_fired(self):
        LogTime()
        coolboy.toggleHeliumValve()
        time.sleep(1)
        
        if coolboy.getHeliumValve():
            print "Helium Valve is Open!"
            self.helium_valve_status = True
        else:
            print "Helium Valve is Closed!"
            self.helium_valve_status = False                                     


    pump_status = Bool(coolboy.isPumping(), label = "Pump is Running:")    
    btnTogglePump = Button("Toggle Pump (Not Working!)")
    
    def _btnTogglePump_fired(self):
        LogTime()
        coolboy.togglePump()
        time.sleep(1)
        
        if coolboy.isPumping():
            print "Pump is Running!"
            self.pump_status = True
        else:
            print "Pump is Stopped!"
            self.pump_status = False
                                                                                                                                                                                                                        
    turbo_freq = Float(coolboy.getTurbopumpFrequency(), label = "Turbopump Frequency (Hz):")
    
    t_user_toset = Float(coolboy.getUserTemperature(), label = "Sample Temperature Set Point:")
    btnSetUserTemp = Button("Set Sample Temperature")
    def _btnSetUserTemp_fired(self):
        LogTime()
        coolboy.setUserTemperature(self.t_user_toset)
        print "Set User Temp. to "+str(self.t_user_toset)
        
    temp_ramp_rate = Float(1, label = "Temp. Ramp Rate (K/min):")
    btnRampUserTemp = Button("Ramp Sample Temperature")
    ramp_temp_thread = Instance(RampTempThread)
        
    def _btnRampUserTemp_fired(self):
        LogTime()
        print "Ramp Sample Temp. to "+str(self.t_user_toset)+" at "+str(self.temp_ramp_rate)
        if self.ramp_temp_thread and self.ramp_temp_thread.isAlive():
            self.ramp_temp_thread.wants_abort = True
        else:
            print "Start Ramping Temp!"
            self.ramp_temp_thread = RampTempThread()
            self.ramp_temp_thread.wants_abort = False
            self.ramp_temp_thread.temp_set = self.t_user_toset
            self.ramp_temp_thread.ramp_rate = self.temp_ramp_rate
            self.ramp_temp_thread.start()                           

    VTI_heater_power = Float(0, label = "VTI Heater Power (W):")
    btnSetVTIHeaterPower = Button("Set VTI Heater Power")
        
    def _btnSetVTIHeaterPower_fired(self):
        LogTime()
        print "VTI Heater Power set to "+str(self.VTI_heater_power)+"Watt."
        coolboy.setVTIHeaterPower(self.VTI_heater_power)
  
            
    sample_heater_status = Bool(coolboy.isSampleHeaterOn(), label = "Sample Heater On:")    
    btnToggleSampleTempControl = Button("Toggle Sample Temperature Control")

        
    def _btnToggleSampleTempControl_fired(self):
        LogTime()
        coolboy.toggleSampleTemperatureControl()
        time.sleep(1)
        
        if coolboy.isSampleHeaterOn():
            print "Sample heater is On!"
            self.sample_heater_status = True
        else:
            print "Sample heater is Off!"
            self.sample_heater_status = False
    
    # Select Update Time Interval
    interval = Enum(1, 3, 10, 30, 60, label="Update Interval (s)")

    # UpdateThread
    update_thread = Instance(UpdateThread)
    
    btnStartUpdate = Button("Start/Stop Update")

    
    def _btnStartUpdate_fired(self):
        if self.update_thread and self.update_thread.isAlive():
            self.update_thread.wants_abort = True
        else:
            LogTime()
            print "Start Update!"
            self.update_thread = UpdateThread()
            self.update_thread.wants_abort = False
            self.update_thread.viewer_t_user = self.viewer_t_user
            self.update_thread.viewer_t_sample = self.viewer_t_sample
            self.update_thread.viewer_t_magnet = self.viewer_t_magnet
            self.update_thread.viewer_t_vti = self.viewer_t_vti
            self.update_thread.viewer_mag_field_setpoint = self.viewer_mag_field_setpoint
            self.update_thread.viewer_mag_field = self.viewer_mag_field
            self.update_thread.viewer_pressure = self.viewer_pressure
            self.update_thread.viewer_sample_heater_power = self.viewer_sample_heater_power
            
            
            self.update_thread.interval = self.interval
            self.update_thread.time_data = self.time_data
            self.update_thread.t_user_data = self.t_user_data
            self.update_thread.t_sample_data = self.t_sample_data
            self.update_thread.t_sample = self.t_sample
            self.update_thread.t_magnet_data = self.t_magnet_data
            self.update_thread.t_vti_data = self.t_vti_data
            self.update_thread.mag_field_setpoint_data = self.mag_field_setpoint_data
            self.update_thread.mag_field_data = self.mag_field_data
            self.update_thread.pressure_data = self.pressure_data
            self.update_thread.sample_heater_power_data = self.sample_heater_power_data
            
            # Give thread access to all the parameters in its parent window
            self.update_thread.parent = self
            
            self.update_thread.start()    
      
    btnSave = Button("Save Data")
    file_name = String()
    
    def _btnSave_fired(self):
        
        for data in self.all_data:
            np.savetxt(self.file_name+"_"+data.name+".txt", data.info)
            
        LogTime()
        print "Data Saved."      
    
    btnDisconnectAD1100 = Button("Disconnect AttoDry1100")
    
    def _btnDisconnectAD1100_fired(self):
        # Time Stamp in Log
        LogTime()
        coolboy.disconnectAndCloseServer()
        sys.stdout = orig_stdout
        f.close()
        
    pop_up1 = Instance(TMC.MainWindow)
    
    def _pop_up1_default(self):
        return TMC.MainWindow()
    
    btnGetTMC = Button("Activate Transport Measurement Console")
    
    def _btnGetTMC_fired(self):
        # Time Stamp in Log
        LogTime()
        print "Activate Transport Measurement Console!"
        self.pop_up1.configure_traits()  
    
    pop_up2 = Instance(TempMagDependenceWindow)
    
    def _pop_up2_default(self):
        return TempMagDependenceWindow()
    
    btnGetTMD = Button("Activate Temperature / Magnetic Field Dependence")

    def _btnGetTMD_fired(self):
        # Time Stamp in Log
        LogTime()
        print "Activate Temperature / Magnetic Field Dependence Console!"
        self.pop_up2.buzzy = MCC.buzzy
        self.pop_up2.configure_traits()  

    pop_up3 = Instance(MCC.MainWindow)
    
    def _pop_up3_default(self):
        return MCC.MainWindow()
    
    btnGetMCC = Button("Activate Magnet Control Console")    
            
    def _btnGetMCC_fired(self):
        # Time Stamp in Log
        LogTime()
        print "Activate Magnet Control Console!"
        self.pop_up3.configure_traits()      
        
    view = View(
                Group(
                      Group(
                            Item('viewer_t_user', style='custom', show_label=True),
                            Item('t_user', style="readonly"),
                            show_border = True,
                            ),                
                      Group(
                            Item('viewer_t_sample', style='custom', show_label=True),
                            Item('t_sample', style="readonly"),
                            show_border = True,
                            ),
                      Group(
                            Item('viewer_t_magnet', style='custom', show_label=True),
                            Item('t_magnet', style="readonly"),
                            show_border = True,
                            ),
                      Group(
                            Item('viewer_t_vti', style='custom', show_label=True),
                            Item('t_vti', style="readonly"),
                            show_border = True,
                            ),                                                        
                      orientation = "horizontal"
                      ),
                Group(
                      Group(
                            Item('viewer_mag_field_setpoint', style='custom', show_label=True),
                            Item('mag_field_setpoint', style="readonly"),
                            show_border = True,
                            ),                
                      Group(
                            Item('viewer_mag_field', style='custom', show_label=True),
                            Item('mag_field', style="readonly"),
                            show_border = True,
                            ),
                      Group(
                            Item('viewer_pressure', style='custom', show_label=True),
                            Item('pressure', style="readonly"),
                            show_border = True,
                            ),
                      Group(
                            Item('viewer_sample_heater_power', style='custom', show_label=True),
                            Item('sample_heater_power', style="readonly"),
                            show_border = True,
                            ),                                                        
                      orientation = "horizontal",
                      ), 
                Group(
                      Group(
                            Item('vti_heater_power', style="readonly", show_label=True),
                            Item('turbopump_freq', style="readonly", show_label = True),
                            Item('p_gain', style="readonly", show_label = True),
                            Item('i_gain', style="readonly", show_label = True),
                            Item('d_gain', style="readonly", show_label = True),
                            show_border = True,
                            orientation = "horizontal"),
                      Group(Item('error_message', style="readonly", show_label = True),
                            Item('btnLowerError', show_label = False),
                            show_border = True,),
                      Group(Item('action_message', style="readonly", show_label = True),
                            show_border = True,),
                      label = "Status",
                      show_border = True,
                      orientation = "vertical",
                      ),
                Group(
                      Group(Item('inner_volume_valve_status', style="readonly", show_label = True),                                     
                            Item('btnToggleInnerVolumeValve',show_label = False),
                            orientation = "vertical",
                            show_border = True),
                      Group(Item('outer_volume_valve_status', style="readonly", show_label = True),                                     
                            Item('btnToggleOuterVolumeValve',show_label = False),
                            orientation = "vertical",
                            show_border = True),
                      Group(Item('pump_valve_status', style="readonly", show_label = True),                                     
                            Item('btnTogglePumpValve',show_label = False),
                            orientation = "vertical",
                            show_border = True),
                      Group(Item('helium_valve_status', style="readonly", show_label = True),                                     
                            Item('btnToggleHeliumValve',show_label = False),
                            orientation = "vertical",
                            show_border = True), 
                      Group(Item('pump_status', style="readonly", show_label = True), 
                            Item('turbo_freq', style="readonly", show_label = True),                                    
                            Item('btnTogglePump',show_label = False),
                            orientation = "vertical",
                            show_border = True),                             
                      orientation = "horizontal",
                      show_border = True,
                      label = "Vacuum Control",                            
                      ),
                Group(
                      Group(Item('t_user_toset', style="simple", show_label = True),                                     
                            Item('btnSetUserTemp',show_label = False),
                            orientation = "vertical",
                            show_border = True),
                      Group(Item('temp_ramp_rate', style="simple", show_label = True),                                     
                            Item('btnRampUserTemp',show_label = False),
                            orientation = "vertical",
                            show_border = True),                                             
                      Group(Item('sample_heater_status', style="readonly", show_label = True),                                     
                            Item('btnToggleSampleTempControl',show_label = False),
                            orientation = "vertical",
                            show_border = True),
                      Group(Item('VTI_heater_power', style="simple", show_label = True),                                     
                            Item('btnSetVTIHeaterPower',show_label = False),
                            orientation = "vertical",
                            show_border = True),                                                              
                      orientation = "horizontal",
                      show_border = True,
                      label = "Temperature Control",                            
                      ),                      
                Group(
                      Item('interval', show_label = True),
                      Item('btnStartUpdate', show_label = False),
                      Item('file_name', width=50),
                      Item('btnSave', show_label = False),
                      orientation = "horizontal",
                      ),
                Group(
                      Item('btnGetTMC', style="custom", show_label = False),
                      Item('btnGetTMD', style="custom", show_label = False),
                      Item('btnGetMCC', style="custom", show_label = False),
                      orientation = "horizontal",
                      ),                
                
                Item('btnDisconnectAD1100', style="custom", show_label = False),                                
                resizable = True,
                title = "AttoDry1100 Control Console")
        
        
main = MainWindow()
main.configure_traits()
