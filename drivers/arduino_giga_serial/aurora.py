#%%

## Serial for arduino communication
## Please upload arduino sketch serial_listning.ino
import serial

## Port for Arduino
COM_port = 'COM4'

## Baud rate. Must match specified in the uploaded Arduino sketch
baud_rate = 115200

## Timeout when calling Arduino
timeout = 0.1

## Laser to pin dicts for different chip configurations
laser_to_pin = {
    'johannes' : {0 : '22',
                  1 : '24',
                  2 : '26'},
    'sigge' : {
               0 : '35',
               1 : '33',
               2 : '31',
               3 : '29',
               4 : '41',
               5 : '43',
               }
    }


## ArdUino contRoller fOR lAsers
class aurora:
    def __init__(self, chip_name):
        self.chip = self.create_chip(laser_to_pin[chip_name])
        
        
    def create_chip(self, laser_to_pin):
        chip = {}
        for laser in laser_to_pin.keys():
            chip[laser] = {'pin': laser_to_pin[laser],
                                'state': 0}
        
        return chip
        
    def switch_to_laser(self, laser_on):
        for laser in self.chip.keys():
            if laser == laser_on:
                self.chip[laser]['state'] = 1
            else:
                self.chip[laser]['state'] = 0
                
        self.update_chip_state()
        
    def turn_off_all_lasers(self):
        self.modify_all_lasers(0)
        
    def turn_on_all_lasers(self):
        self.modify_all_lasers(1)
        
    def modify_all_lasers(self, on_or_off):
        for laser in self.chip.keys():
            self.chip[laser]['state'] = on_or_off
                
        self.update_chip_state()
        
    def update_chip_state(self):
        arduino = serial.Serial(COM_port, baud_rate, timeout=timeout)
        for laser in self.chip.keys():
            command = self.create_command_from_key(laser)
            arduino.write(command)
        arduino.close()
        
        
    def send_command(self, command):
        arduino = serial.Serial(COM_port, baud_rate, timeout=timeout)
        arduino.write(command.encode())
        arduino.close()
        
    def create_command_from_key(self, key):
        pin = str(self.chip[key]['pin'])
        state = str(self.chip[key]['state'])
        return (pin + state).encode()
        
        
        
johannes = aurora('sigge')
# johannes.switch_to_laser(1)
johannes.turn_on_all_lasers()
# johannes.turn_off_all_lasers()