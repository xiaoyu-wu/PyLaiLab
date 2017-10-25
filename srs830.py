import visa

class SRS830():
    
    def __init__(self, GPIB_number):
        rm = visa.ResourceManager()
        tempstr = 'GPIB0::'+str(GPIB_number)+'::INSTR'
        self.instrument = rm.open_resource(tempstr)
        self.X = 0
        self.Y = 0
        self.R = 0
        self.Theta = 0
        self.aux_out = [0,0,0,0]
        
    def outp(self, i):
        # This function UPDATES the attributes (X, Y, R, Theta). To read the value, call those attributes.
        # i=1 for X, 2 for Y, 3 for R, 4 for theta
        self.instrument.write("OUTP? "+str(i))
        value = float(self.instrument.read())
        OutputDictionary = {1:"X", 2:"Y", 3:"R", 4:"Theta"}
        setattr(self, OutputDictionary[i], value) 
        return value
        
    def set_aux_out(self, i, voltage):
        # Set aux out i to voltage
        if (voltage>=-10.5 and voltage <=10.5):
            tempstr = "AUXV "+str(i)+", "+str(voltage)
            self.instrument.write(tempstr)
            self.aux_out[i-1] = voltage
        return
        
    def get_aux_in(self, i):
        # Get aux in i value
        self.instrument.write("OAUX? "+str(i))
        aux_in = float(self.instrument.read())
        return aux_in
        
    
        

