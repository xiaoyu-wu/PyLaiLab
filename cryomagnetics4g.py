import visa
import string

# 0.19306 Tesla per Amp
field2current = 0.19306

class Cryomagnetics4G():
    
    def __init__(self, com_address):
        rm = visa.ResourceManager()
        tempstr = 'COM'+str(com_address)
        self.instrument = rm.open_resource(tempstr)
        self.instrument.write("REMOTE")
        self.instrument.read()
        
    def queryPersistentSwitchHeater(self):
        try:
            self.instrument.write("PSHTR?")
            # Dispose the echo
            junkstr = self.instrument.read()
            # This is the real feedback
            tempstr = self.instrument.read()
            tempstr_2 = tempstr.rstrip()
            tempint = int(tempstr_2[0])
            return bool(tempint)
        except ValueError:
            print "Value Error!"
        else:
            print "Error Unknown!"
            
    
    def queryMagnetCurrent(self):
        # return Magnetic Field in Tesla
        
        self.instrument.write("IMAG?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("kG","")
        tempstr = tempstr.rsplit()
        # 10 for conversion from kG to T
        i_mag = float(tempstr[0])/10.0
        self.i_mag = i_mag
        return i_mag
        
    def queryMagnetVoltage(self):
        # return Magnet Voltage in Volt
        
        self.instrument.write("VMAG?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("V","")
        tempstr = tempstr.rsplit()
        v_mag = float(tempstr[0])
        return v_mag            
    
    def queryOutputCurrent(self):
        # return Output Current in Tesla
        
        self.instrument.write("IOUT?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("kG","")
        tempstr = tempstr.rsplit()
        # 10 for conversion from kG to T
        i_out = float(tempstr[0])/10.0
        return i_out
        
    def queryOutputVoltage(self):
        # return Output Voltage in Volt
        
        self.instrument.write("VOUT?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("V","")
        tempstr = tempstr.rsplit()
        v_out = float(tempstr[0])
        return v_out
        
    def querySweepMode(self):
        
        self.instrument.write("SWEEP?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.rsplit()
        return tempstr[0]
        
    def queryUpperLimit(self):

        self.instrument.write("ULIM?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("kG","")
        tempstr = tempstr.rsplit()
        upper_limit = float(tempstr[0])/10.0
        return upper_limit        

    def queryLowerLimit(self):

        self.instrument.write("LLIM?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("kG","")
        tempstr = tempstr.rsplit()
        lower_limit = float(tempstr[0])/10.0
        return lower_limit
    
    def queryVoltageLimit(self):
        self.instrument.write("VLIM?")
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback
        tempstr = self.instrument.read()
        tempstr = tempstr.replace("V","")
        tempstr = tempstr.rsplit()
        v_lim = float(tempstr[0])
        return v_lim
        
    def queryRateLimit(self, range_number):
        self.instrument.write("RATE? "+str(range_number))
        # Dispose the echo
        junkstr = self.instrument.read()
        # This is the real feedback, ramp rate limit in amps/sec
        rate_limit = float(self.instrument.read())
        # convert the rate from amps/sec to T/min
        rate_limit *= (field2current * 60)
        return rate_limit
        
    def setRate(self, range_number, sweep_rate):
        sweep_rate /= (field2current*60)
        if (range_number == 0):
            if sweep_rate > 0.03:
                sweep_rate = 0.03
                print "Sweep Rate requested is too high!"
        elif (range_number == 1):
            if sweep_rate > 0.01:
                sweep_rate = 0.01
                print "Sweep Rate requested is too high!"
        else:
            print "Range requested unavailable!"
            return
        tempstr = "RATE "+str(range_number)+" "+str(sweep_rate)
        self.instrument.write(tempstr)
        self.instrument.read()
        
    def setPersistentSwitchHeater(self, state):
        if (state == "ON"):
            i_mag = self.queryMagnetCurrent()
            i_out = self.queryOutputCurrent()
            if (i_mag != i_out):
                print "Cannot turn ON heater with inequal Magnet Current and Output Current!!!"
                return
        elif (state == "OFF"):
            pass
        else:
            print "Invalid Heater State! (ON/OFF only)"
            return 
        self.instrument.write("PSHTR "+state)
        self.instrument.read()

    def setSweepMode(self, sweep_mode):
        sweep_mode_range = ["UP", "DOWN", "PAUSE", "ZERO"]
        if (sweep_mode in sweep_mode_range):
            self.instrument.write("SWEEP "+sweep_mode)
            self.instrument.read()
        else:
            print "Invalid Sweep Mode!"
            return
            
    def setUpperLimit(self, upper_limit):
        upper_limit *= 10
        self.instrument.write("ULIM "+str(upper_limit))
        self.instrument.read()
        
    def setLowerLimit(self, lower_limit):
        lower_limit *= 10
        self.instrument.write("LLIM "+str(lower_limit))
        self.instrument.read()                    
                                                                                                                                                            