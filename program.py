import sys
import os
import time

# Add the path to the 'python-OBD-master' directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'python-OBD-master'))

import obd as obd
from obd.utils import bytes_to_int
# obd.logger.setLevel(obd.logging.DEBUG) # enables all debug information
# from obd import OBD, OBDStatus

print("Started program")

from config import debug_mode, metrics_file

import RGB1602
lcd=RGB1602.RGB1602(16,2)
lcd.clear()
lcd.setCursor(0, 0)
lcd.printout("Looking for car")
lcd.setRGB(255, 255, 255);

tick = False #it will blink a star to show it's not stuck

blank = [0,0,0,0,0,0,0,0]

smiley_face = [
    0b00000,  # Row 1
    0b01010,  # Row 2 (eyes)
    0b01010,  # Row 3 (eyes)
    0b00000,  # Row 4 (empty row)
    0b10001,  # Row 5 (mouth)
    0b01110,  # Row 6 (mouth)
    0b00000,  # Row 7 (empty row)
    0b00000   # Row 8 (empty row)
]

degrees = [
    0b01110,
    0b10001,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
    0b00000
]

lcd.load_custom_char(0, blank)
lcd.load_custom_char(1, smiley_face)
lcd.load_custom_char(2, degrees)

connected = False
connection = obd.Async()
while not connected:
    connection = obd.Async() #setup async connection

    lcd.setCursor(0, 0)

    if(connection.status() == obd.OBDStatus.NOT_CONNECTED):
        lcd.setRGB(255,0,0);
        lcd.printout("No car found!   ")
        lcd.setCursor(0, 1)
        lcd.printout("No reader.      ")
        
        if tick:
            lcd.setCursor(15,1)
            lcd.write(0)
            tick = False
        else:
            lcd.setCursor(15,1)
            lcd.write(1)
            tick = True

    elif(connection.status() == obd.OBDStatus.ELM_CONNECTED):
        lcd.setRGB(255,0,0);
        lcd.printout("No car found!   ")
        lcd.setCursor(0, 1)
        lcd.printout("Found reader    ")

        if tick:
            lcd.setCursor(15,1)
            lcd.write(0)
            tick = False
        else:
            lcd.setCursor(15,1)
            lcd.write(1)
            tick = True

    elif(connection.status() == obd.OBDStatus.OBD_CONNECTED or connection.status() == obd.OBDStatus.CAR_CONNECTED):
        lcd.setRGB(0, 255, 0);
        lcd.printout("Found car!      ")
        lcd.setCursor(0, 1)
        lcd.printout("Initialising.   ")

        connected = True

    time.sleep(0.5)

lcd.clear()

class Metric():
    def __init__(self, name, unit, calculation_function, commands):
        self.name = name #name of the metric
        self.unit = unit #unit it is measured in
        self.commands = commands #any commands to issue to the car to get values we want
        self.calculation_function = calculation_function # help us combine multiple values or do maths to get a useful number

    def setup(self):
        global connection
        for command in self.commands:
            connection.watch(command)

    def getValue(self):
        global connection
        values = []
        for command in self.commands:
            response = connection.query(command) # subscribe to each metric we need from the car
            if response.is_null(): #if the car dosen't support it, set it to 0 so the true value is always 0.
                values.append(0)
            else:
                values.append(response.value.magnitude)

        if self.calculation_function:
            return self.calculation_function(values)
        else:
            return values[0]

    def printValue(self):
        str(self.getValue()) + self.unit

def kph_to_mph(values):
    return values[0] / 1.609344

def to_torque(messages):
    """ decoder for Torque messages """
    d = messages[0].data # only operate on a single message
    d = d[2:] # chop off mode and PID bytes
    v = bytes_to_int(d) # helper function for converting byte arrays to ints
    return v

torque_command = obd.OBDCommand("Torque", "Engine Torque", b"0163", 2, to_torque)

def calc_power(values):
    rpm = values[0]
    torque = values[1]
    return (rpm * torque) / 5252

metrics = {
    "coolant_temp": Metric("coolant", "°C", None, [obd.commands.COOLANT_TEMP]),
    "rpm": Metric("rpm", "rpm", None, [obd.commands.RPM]),
    "speed": Metric("speed", "mph", kph_to_mph, [obd.commands.SPEED]),
    "maf": Metric("air", "g/s", None, [obd.commands.MAF]),
    "fuel_level": Metric("fuel", "%", None, [obd.commands.FUEL_LEVEL]),
    "air_temp": Metric("air temp", "°C", None, [obd.commands.AMBIANT_AIR_TEMP]),
    "oil_temp": Metric("oil temp", "°C", None, [obd.commands.OIL_TEMP]),
    "fuel_rate": Metric("fuel rate", "L/h", None, [obd.commands.FUEL_RATE]),
    "torque": Metric("torque", "Nm", None, [torque_command]),
    "power": Metric("power", "hp", calc_power, [obd.commands.RPM, torque_command])
}

file_metrics = open(metrics_file, "r").read().splitlines()

active_metrics = []
for file_metric in file_metrics: # for each monitored metric in the file
    metrics[file_metric].setup()
    active_metrics.append(metrics[file_metric]) # add it to current monitored metrics

connection.start()

def printout_custom_char(lcd, string, row):
    instructions = []
    params = []

    accumulated = ""

    for char in string:
        if char != "°":
            accumulated = accumulated + char
        else:
            instructions.append("printout")
            params.append(accumulated)
            accumulated = ""
            instructions.append("write")
            params.append("2")

    if string[len(string) - 1] != "°":
        instructions.append("printout")
        params.append(accumulated)

    position = 0
    count = 0

    for instruction in instructions:
        if instruction == "printout":
            lcd.setCursor(position, row)
            lcd.printout(params[count])
            position = position + len(params[count])
        
        elif instruction == "write":
            lcd.write(2)
            position = position + 1

        count = count + 1

while True:
    metric1 = active_metrics[0]
    metric1 = active_metrics[1]
    metric1 = active_metrics[2]
    metric1 = active_metrics[3]

    metric1

    value1 = "90°C"
    value2 = "987rpm"
    value3 = "5.1L/h"
    value4 = "56HP"

    value1_length = len(value1)
    value2_length = len(value2)
    value3_length = len(value3)
    value4_length = len(value4)

    blank_space_row0 = " " * (lcd.width - (value2_length + value1_length))
    printout_custom_char(lcd, value1 + blank_space_row0 + value2, 0)

    blank_space_row1 = " " * (lcd.width - (value4_length + value3_length))
    printout_custom_char(lcd, value3 + blank_space_row0 + value4, 1)

    # blank_space_row0 = " " * (lcd.width - (value2_length + value1_length))
    # lcd.setCursor(0,0)
    # lcd.printout(value1 + blank_space_row0 + value2)

    # blank_space_row1 = " " * (lcd.width - (value4_length + value3_length))
    # lcd.setCursor(0,1)
    # lcd.printout(value3 + blank_space_row0 + value4)

    time.sleep(0.5)