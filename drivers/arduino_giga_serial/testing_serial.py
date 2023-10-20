import time
import serial


def test():
    print("Sent")
    arduino = serial.Serial('COM4', 115200, timeout=.1)
    time.sleep(1)
    arduino.write('221'.encode())
    arduino.write('241'.encode())
    arduino.write('261'.encode())
    time.sleep(1)
    arduino.write('220'.encode())
    arduino.write('240'.encode())
    arduino.write('260'.encode())
    arduino.close()
    
test()