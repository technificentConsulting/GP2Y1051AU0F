#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import serial

class AIRQ():
    """
    This program will read the data from Sharp GP2Y1051AU0F dust density sensor.
    The device will keep sending 7 bytes serial data every 10ms.
    For example:
    AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63
    FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF ... ...

    The useful data chunk is formatted as:
    AA 00 02 00 61 63 FF

    Where represents AA represents the begining byte, FF represents the ending byte.

    Second byte 00 is the Vout high, third byte 02 is the Vout low
    """
    def __init__(self, ser):
        self.ser = ser

        # The device will keep sending 7 bytes data every 100ms
        self.serial_measure_bytes = 7

        # Read the chunk of the serial data, 2 times of the device output
        self.serial_expanded_measure_bytes = self.serial_measure_bytes * 2

    def get_serial_chunk(self):

        # read bytes from serial, we read the larger chunk(14 bytes) rather than 7 bytes.
        data = self.ser.read(self.serial_expanded_measure_bytes).encode('hex')

        # use all the rest of the data, we want to use the real time value
        data += self.ser.readline(self.ser.inWaiting()).encode('hex')

        if not data:
            return False

        try:
            # find out the first aa postion
            aa_index = data.index('aa')
        except ValueError:
            time.sleep(1)

        # The data is a string not a hex array, so we need to count the
        # element as charachater, 1 hex byte contains 2 charachaters
        ff_index = aa_index + self.serial_measure_bytes * 2

        # Get the formmated chunk which start from AA, end with FF
        formatted_chunk = data[aa_index:ff_index]

        return formatted_chunk

    def num_format(self, num_hex):
        """
        Convert Hex value to decimal
        """
        num_int = int(num_hex, 16)
        num_int = float(format(num_int, '.10f'))
        return num_int

    def get_vout(self, byte_data):
        # byte_data = self.get_serial_chunk()

        if not byte_data:
            return -1

        data_array = byte_data.decode('hex')
        vout_h = self.num_format(data_array[1].encode('hex'))
        vout_l = self.num_format(data_array[2].encode('hex'))

        # print "VoutH: " + str(vout_h)
        # print "VoutL: " + str(vout_l)

        # Caculate the Vout
        # 0 - 5V mapped to 0 - 1023 integer values
        vout = ((vout_h * 256) + vout_l) * 5 / 1024
        # print float(format(vout, '%.3f'))
        vout = round(vout, 4)
        return vout

    def get_k(self, vout):

        """
        K represents a specific coefficient for the GP2Y1051AU0F dust sensor.
        The value of K will vary from the given value of Vout
        The conditions are searched from the internet, so it might be not correct.
        """
        if vout < 0.046:
            return 200
        elif vout < 0.049:
            return 400
        elif vout < 0.052:
            return 600
        elif vout < 0.055:
            return 750
        elif vout < 0.059:
            return 900
        elif vout < 0.065:
            return 1000
        elif vout < 0.071:
            return 1250
        elif vout < 0.076:
            return 1400
        elif vout < 0.081:
            return 1700
        elif vout < 0.086:
            return 1800
        elif vout < 0.091:
            return 1900
        elif vout < 0.101:
            return 2000
        elif vout < 0.111:
            return 2200
        else:
            return 3000

    def get_density(self, vout):

        k = self.get_k(vout)

        # Dust density, unit: ug/m3
        density = int(k * vout)
        return density


if __name__ == '__main__':

    def show(aq):
        byte_data = aq.get_serial_chunk()
        vout = aq.get_vout(byte_data)
        # print "vout: " + str(vout)
        if not byte_data:
            print "Waiting for serial data..."

        # print "line: " + chunk
        # print "in_waiting: " + str(aq.ser.in_waiting) + " byte(s)"

        k = aq.get_k(vout)
        density = aq.get_density(vout)

        sys.stdout.write("[ %s | K: %s | Vout: %s V | Dust density: %s ug/m3 ] \r" % ( byte_data, k, vout, density))
        sys.stdout.flush()
        time.sleep(1)

    try:
        ser = serial.Serial(
            port = 'COM7', # COM7 for windows
            baudrate = 2400,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1
        )

        aq = AIRQ(ser)
        while 1:
            show(aq)
            # data = aq.get_serial_chunk()
            # vout = aq.get_vout()
            # density = aq.get_density(vout)
            # if data:
            #     print data
            #     print vout
            #     print density
            #     time.sleep(1)
            # else:
            #     print "waiting for serial data"
    except KeyboardInterrupt:
        ser.close()
        print "\nQuit!"
