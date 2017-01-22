from ctypes import *
import time

adlib = cdll.LoadLibrary("E:/Python Programs/attoDRY1100Interface.dll")

class AttoDry1100():
    def __init__(self, COM_port):
        # Begin must be called first to start AttoDry interface server. 
        # Argument 0 stands for AttoDry1100, 1 for AttoDry2100 
        self.e = adlib.Begin(0, None, None)
        if self.e:
            adlib.End()
            print "Error in Function: Begin!"
            return
        print "Server Begined."
        
        self.e = adlib.Connect("COM"+str(COM_port))
        if self.e:
            adlib.End()
            print "Error in Function: Connect!"
            return
        print "Port Connected."

        device_initialized = c_bool()
        while (not device_initialized.value):
            self.e = adlib.IsDeviceInitialised(byref(device_initialized))
            if self.e:
                self.disconnectAndCloseServer()
                return
        print "AttoDry has been initialized."
                        
    
    def disconnectAndCloseServer(self):
        self.e = adlib.Disconnect()
        print "Disconnected."
        self.e = adlib.End()
        print "Server Closed."
        
    def getSampleTemperature(self):
        self.sample_temp = c_float()
        self.e = adlib.GetSampleTemperature(byref(self.sample_temp))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetSampleTemperature!"
            return
        return self.sample_temp.value
        
    def getMagnetTemperature(self):
        self.magnet_temp = c_float()
        self.e = adlib.Get4KStageTemperature(byref(self.magnet_temp))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetMagnetTemperature!"
            return
        return self.magnet_temp.value
        
    def getVtiTemperature(self):
        self.vti_temp = c_float()
        self.e = adlib.GetVtiTemperature(byref(self.vti_temp))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetVtiTemperature!"
            return
        return self.vti_temp.value
        
    def getUserTemperature(self):
        self.user_temp = c_float()
        self.e = adlib.GetUserTemperature(byref(self.user_temp))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetUserTemperature!"
            return
        return self.user_temp.value
        
    def setUserTemperature(self, set_value):
        self.user_temp = c_float(set_value)
        self.e = adlib.SetUserTemperature(self.user_temp)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetUserTemperature!"
            return
        return self.user_temp.value

    def setVTIHeaterPower(self, set_value):
        self.VTI_heater_power = c_float(set_value)
        self.e = adlib.SetVTIHeaterPower(self.VTI_heater_power)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetVTIHeaterPower!"
            return
        return self.VTI_heater_power.value               
                                                
    def getActionMessage(self):
        self.action_message = c_char_p()
        # Message length = 500
        self.e = adlib.GetActionMessage(self.action_message, 500)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetActionMessage!"
            return
        return self.action_message.value
        
    def getAttodryErrorMessage(self):
        self.error_message = c_char_p()
        # Message length = 500
        self.e = adlib.GetAttodryErrorMessage(self.error_message, 500)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetAttodryErrorMessage!"
            return
        return self.error_message.value
    
    def setUserMagneticField(self, set_value):
        self.user_mag_field = c_float(set_value)
        self.e = adlib.SetUserMagneticField(self.user_mag_field)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetUserMagneticField!"
            return
        return self.user_mag_field.value
        
    def getMagneticField(self):
        self.mag_field = c_float()
        self.e = adlib.GetMagneticField(byref(self.mag_field))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetMagneticField!"
            return
        return self.mag_field.value                
        
    def getMagneticFieldSetPoint(self):
        self.mag_field_setpoint = c_float()
        self.e = adlib.GetMagneticFieldSetPoint(byref(self.mag_field_setpoint))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetMagneticFieldSetPoint!"
            return
        return self.mag_field_setpoint.value 
        
    def getPressure(self):
        self.pressure = c_float()
        self.e = adlib.GetPressure(byref(self.pressure))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in getPressure!"
            return
        return self.pressure.value
        
    def getTurbopumpFrequency(self):
        self.turbo_freq = c_float()
        self.e = adlib.GetTurbopumpFrequency(byref(self.turbo_freq))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetTurbopumpFrequency!"
            return
        return self.turbo_freq.value
        
    def getSampleHeaterPower(self):
        self.sample_heater_power = c_float()
        self.e = adlib.GetSampleHeaterPower(byref(self.sample_heater_power))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetSampleHeaterPower!"
            return
        return self.sample_heater_power.value  
        
    def getVtiHeaterPower(self):
        self.vti_heater_power = c_float()
        self.e = adlib.GetVtiHeaterPower(byref(self.vti_heater_power))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetVtiHeaterPower!"
            return
        return self.vti_heater_power.value
        
    def getProportionalGain(self):
        self.proportional_gain = c_float()
        self.e = adlib.GetProportionalGain(byref(self.proportional_gain))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetProportionalGain!"
            return
        return self.proportional_gain.value
        
    def getIntegralGain(self):
        self.integral_gain = c_float()
        self.e = adlib.GetIntegralGain(byref(self.integral_gain))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetIntegralGain!"
            return
        return self.integral_gain.value
        
    def getDerivativeGain(self):
        self.derivative_gain = c_float()
        self.e = adlib.GetDerivativeGain(byref(self.derivative_gain))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetDerivativeGain!"
            return
        return self.derivative_gain.value

    def setProportionalGain(self, set_value):
        self.proportional_gain = c_float(set_value)
        self.e = adlib.SetProportionalGain(self.proportional_gain)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetProportionalGain!"
            return
        return self.proportional_gain.value         

    def setIntegralGain(self, set_value):
        self.integral_gain = c_float(set_value)
        self.e = adlib.SetIntegralGain(self.integral_gain)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetIntegralGain!"
            return
        return self.integral_gain.value                        

    def setDerivativeGain(self, set_value):
        self.derivative_gain = c_float(set_value)
        self.e = adlib.SetDerivativeGain(self.derivative_gain)
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in SetDerivativeGain!"
            return
        return self.derivative_gain.value                                                                         
                                                                                                                                                                                                                        
    def lowerError(self):
        self.e = adlib.LowerError()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in LowerError!"
            return
        return
        
    def getInnerVolumeValve(self):
        # Return True for Opened Valve, False for Closed Valve
        self.inner_volume_valve_open = c_bool()
        self.e = adlib.GetInnerVolumeValve(byref(self.inner_volume_valve_open))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetInnerVolumeValve!"
            return
        return self.inner_volume_valve_open
    
    def toggleInnerVolumeValve(self):
        self.e = adlib.ToggleInnerVolumeValve()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in ToggleInnerVolumeValve!"
            return
        return
        
    def getOuterVolumeValve(self):
        # Return True for Opened Valve, False for Closed Valve
        self.outer_volume_valve_open = c_bool()
        self.e = adlib.GetOuterVolumeValve(byref(self.outer_volume_valve_open))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetOuterVolumeValve!"
            return
        return self.outer_volume_valve_open
    
    def toggleOuterVolumeValve(self):
        self.e = adlib.ToggleOuterVolumeValve()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in ToggleOuterVolumeValve!"
            return
        return
        
    def getPumpValve(self):
        # Return True for Opened Valve, False for Closed Valve
        self.pump_valve_open = c_bool()
        self.e = adlib.GetPumpValve(byref(self.pump_valve_open))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetPumpValve!"
            return
        return self.pump_valve_open
    
    def togglePumpValve(self):
        self.e = adlib.TogglePumpValve()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in TogglePumpValve!"
            return
        return
        
    def getHeliumValve(self):
        # Return True for Opened Valve, False for Closed Valve
        self.helium_valve_open = c_bool()
        self.e = adlib.GetHeliumValve(byref(self.helium_valve_open))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in GetHeliumValve!"
            return
        return self.helium_valve_open
    
    def toggleHeliumValve(self):
        self.e = adlib.ToggleHeliumValve()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in ToggleHeliumValve!"
            return
        return
        
    def isPumping(self):
        # Return True for Pump Running
        self.is_pumping = c_bool()
        self.e = adlib.IsPumping(byref(self.is_pumping))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in IsPumping!"
            return
        return self.is_pumping
    
    def togglePump(self):
        self.e = adlib.TogglePump()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in TogglePump!"
            return
        return
        
    def toggleSampleTemperatureControl(self):
        self.e = adlib.ToggleSampleTemperatureControl()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in ToggleSampleTemperatureControl!"
            return
        return

    def isSampleHeaterOn(self):
        # Return True for Sample Heater On
        self.is_sample_heater_on = c_bool()
        self.e = adlib.IsSampleHeaterOn(byref(self.is_sample_heater_on))
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in IsSampleHeaterOn!"
            return
        return self.is_sample_heater_on

                
    def confirm(self):
        self.e = adlib.Confirm()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in Confirm!"
            return
        return

    def cancel(self):
        self.e = adlib.Cancel()
        if self.e:
            self.disconnectAndCloseServer()
            print "Error in Cancel!"
            return
        return                                                                                                                                                                       