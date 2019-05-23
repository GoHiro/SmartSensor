import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
line = ser.readline()
print(line)
ser.close()
