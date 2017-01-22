import visa
from string import split

# ch[0] for a, ch[1] for b
ch = ['a', 'b']

class K2634B():

    def __init__(self, gpib_address):
        rm = visa.ResourceManager()
        tempstr = 'GPIB0::'+str(gpib_address)+'::INSTR'
        self.instrument = rm.open_resource(tempstr)
        
    def reset(self):
        self.instrument.write('reset()')
        
    def resetChannel(self, channel_num):
        tempstr = 'smu'+ch[channel_num]+'.reset()'
        self.instrument.write(tempstr)
        
    def selectVoltageSourceFuncion(self, channel_num):
        tempstr = 'smu'+ch[channel_num]+'.source.func = smu'+ch[channel_num]+'.OUTPUT_DCVOLTS'
        self.instrument.write(tempstr)
    
    def setVoltageSourceRange(self, channel_num, sourceRange=0):
        if (sourceRange == 0):
            # 0 for Auto
            tempstr = 'smu'+ch[channel_num]+'.source.autorangev = smu'+ch[channel_num]+'.AUTORANGE_ON'
        elif (sourceRange > 0):
            tempstr = 'smu'+ch[channel_num]+'.source.rangev = '+str(sourceRange)
        self.instrument.write(tempstr)
        
    def setVoltageSourceLevel(self, channel_num, sourceLevel):
        tempstr = 'smu'+ch[channel_num]+'.source.levelv = '+str(sourceLevel)
        self.instrument.write(tempstr)
        
    def setCurrentLimit(self, channel_num, currentLimit):
        tempstr = 'smu'+ch[channel_num]+'.source.limiti = '+str(currentLimit)
        self.instrument.write(tempstr)
        
    def setCurrentRange(self, channel_num, currentRange):
        tempstr = 'smu'+ch[channel_num]+'.measure.rangei = '+str(currentRange)
        self.instrument.write(tempstr)
        
    def turnOnOutput(self, channel_num):
        tempstr = 'smu'+ch[channel_num]+'.source.output = smu'+ch[channel_num]+'.OUTPUT_ON'
        self.instrument.write(tempstr)
    
    def readCurrent(self, channel_num):
        tempstr = 'print(smu'+ch[channel_num]+'.measure.i())'
        result = float(self.instrument.query(tempstr))
        return result
    
    def turnOffOutput(self, channel_num):
        tempstr = 'smu'+ch[channel_num]+'.source.output = smu'+ch[channel_num]+'.OUTPUT_OFF'
        self.instrument.write(tempstr)
        
    def displayCurrentMeasurement(self, channel_num):
        tempstr = 'display.smu'+ch[channel_num]+'.measure.func = display.MEASURE_DCAMPS'
        self.instrument.write(tempstr)
            
    def readCurrentAndVoltage(self, channel_num):
        tempstr = 'print(smu'+ch[channel_num]+'.measure.iv())'
        result_string = self.instrument.query(tempstr)
        result_list = split(result_string)
        result = [float(item) for item in result_list]
        return result
    
    def readVoltageLevel(self, channel_num):
        tempstr = 'print(smu'+ch[channel_num]+'.source.levelv)'
        result = float(self.instrument.query(tempstr))
        return result        
        
            
                    