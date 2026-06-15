'''
This module is intended to be the dictionary for the Seren R301 Radio Frequency Power Supply
Author: Kenneth Shepherd Jr
changelog: 

Date Created: 2025/06/03
'''

import serial

# end of line 
CR = b'\r'
LF = b'\n'
CRLF = CR + LF

# Assertions
assert_serial = b'***' + CR

# query commands
query = b'Q' + CR
query_voltage = b'V?' + CR
query_power_lvl = b'LVL?' + CR
query_DC_Bias = b'0?' + CR

# selections
select_voltage_ctrl = b'DR' + CR
select_power_ctrl = b'IR' + CR
select_FWD_PWR = b'DL' + CR
select_load_PWR = b'EL' + CR

# enables
pulse_on = b'+P' + CR
pulse_off = b'-P' + CR
RF_on = b'G' + CR
RF_off = b'S' + CR
echo_on = b'ECHO' + CR
echo_off = b'NOECHO' + CR

# setpoints
set_pwr = b'W' + CR
set_volt = b'V' + CR
set_pulse_DTY = b'D' + CR
set_pulse_HT = b'HT' + CR
set_pulse_LP = b'LP' + CR
set_pulse_HP = b'HP' + CR

class Shutter:
    '''Class to interface with the relay box for shutters'''
    
    def __init__(self, PORT):       
        self.ser = serial.serial_for_url(
            PORT, 
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )

        
    def close_port(self):
        '''Closes the port'''
        self.ser.close()

    def close_shutter_02(self):
        ''''Opens the shutter. Converts the hexidecimal to bytes and opens the shutter'''
        hex_string = '55 56 00 00 00 03 02 b0'
        hex_bytes = bytes.fromhex(hex_string.replace(' ', ""))
        close_shutter = hex_bytes
        self.ser.write(close_shutter)  
        
    def close_shutter_01(self):
        ''''Opens the shutter. Converts the hexidecimal to bytes and opens the shutter'''
        hex_string = '55 56 00 00 00 04 02 b1'
        hex_bytes = bytes.fromhex(hex_string.replace(' ', ""))
        close_shutter = hex_bytes
        self.ser.write(close_shutter)   

    def open_shutter_02(self):
        ''''Opens the shutter. Converts the hexidecimal to bytes and opens the shutter'''
        hex_string = '55 56 00 00 00 03 01 af'
        hex_bytes = bytes.fromhex(hex_string.replace(' ', ""))
        open_shutter = hex_bytes
        self.ser.write(open_shutter)        

    def open_shutter_01(self):
        ''''Opens the shutter. Converts the hexidecimal to bytes and opens the shutter'''
        hex_string = '55 56 00 00 00 04 01 b0'
        hex_bytes = bytes.fromhex(hex_string.replace(' ', ""))
        open_shutter = hex_bytes
        self.ser.write(open_shutter)

        

class R301_Radio_Frequency_Power_Supply:
    '''Class to interface with R301_ Radio Frequency Power Supply'''
    
    def __init__(self, PORT):
        self.ser = serial.serial_for_url(
            PORT, 
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)
        
        self.serial_on()

    def close_port(self):
        '''Closes communication with the Power supply'''
        self.ser.close()
        
    def enable_echo(self):
        '''Turns on echo mode'''
        self.ser.write(echo_on)
        
    def enable_pulse_mode(self):
        '''Turns on the pulse mode'''
        self.ser.write(pulse_on)
        
    def enable_RF_gun(self):
        '''Turns on the RF gun'''
        self.ser.write(RF_on)
        
    def disable_echo(self):
        '''Turns off the echo mode'''
        
    def disable_pulse_mode(self):
        '''Turns of pulse mode'''
        self.ser.write(pulse_off)
        
    def disable_RF_gun(self):
        '''Turns off the RF_gun'''
        self.ser.write(RF_off)
        
    def query_instrument(self):
        '''Queries the instrument'''
        self.ser.write(query)
        response = self.ser.readlines()
#         response = response[0].decode().strip('\r')
#         response = response.split(' ')
#         XXXXXXX = response[0]
#         fwd_power = response[1] # watts
#         ref_power = response[2] # watts
#         max_power = response[3] # watts
        return response #, fwd_power, ref_power, max_power
    
    def set_duty_cycle(self, duty_cycle):
        '''Sets the instruments duty cycle when pulse mode is enabled'''
        duty_cycle = str(duty_cycle).encode()
        command = duty_cyle + b' ' + set_pulse_DTY
        self.ser.write(command)
        
    def set_high_power(self, high_power):
        '''Sets the instrument high time when pulse mode is enabled'''
        high_power = str(high_power).encode()
        command = high_power + b' ' + set_pulse_HP
        self.ser.write(command)
        
    def set_low_power(self, low_power):
        '''Sets the instrument low time when pulse mode is enabled'''
        low_power = str(low_power).encode()
        command = low_power + b' ' + set_pulse_LP
        self.ser.write(command)
        
    def set_high_time(self, high_time):
        '''Sets the instrument high time when pulse mode is enabled'''
        high_time = str(high_time).encode()
        command = high_time + b' ' + set_pulse_HT
        self.ser.write(command)
        
    def set_power(self, power):
        '''Sets the instrument power. Pass power as a string'''
        power = int(power)
        power = str(power).encode()
        command = power + b' ' + set_pwr
        self.ser.write(command)
        
    def set_voltage(self, voltage):
        '''Sets the instruments voltage. Pass the voltage as a string'''
        voltage = str(voltage).encode()
        comannd = voltage + b' ' + set_volt
        self.ser.write(command)        

    def serial_on(self):
        '''Turns on serial communication'''
        self.ser.write(assert_serial)
