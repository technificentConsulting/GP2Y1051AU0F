#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import serial

class AIRQ():
    """
    This program will read the data from Sharp GP2Y1051AU0F dust density sensor.
    The device will keep sending 7 bytes serial data every 100ms.
    For example:
    AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63
    FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF ... ...

    The useful data chunk is formatted as:
    AA 00 02 00 61 63 FF

    Where represents AA represents the begining byte, FF represents the ending byte.

    Second byte 00 is the Vout high
    Third byte 02 is the Vout low
    """
    def __init__(self, ser):
        self.ser = ser

        # The device will keep sending 7 bytes data every 100ms
        self.serial_measure_bytes = 7

        # Read the chunk of the serial data, 2 times of the device output
        self.serial_expanded_measure_bytes = self.serial_measure_bytes * 2

    def get_serial_chunk(self):

        # read bytes from serial, we read the larger chunk(14 bytes) rather than 7 bytes.
        chunk = self.ser.read(self.serial_expanded_measure_bytes).encode('hex')

        # find out the first aa postion
        aa_index = chunk.index('aa')

        # The data is a string not a hex array, so we need to count the
        # element as charachater, 1 hex byte contains 2 charachaters
        ff_index = aa_index + self.serial_measure_bytes * 2

        # Get the formmated chunk which start from AA, end with FF
        formatted_chunk = chunk[aa_index:ff_index]

        return formatted_chunk

    def num_format(self, num_hex):
        num_int = int(num_hex, 16)
        return float(format(num_int, '.10f'))

    def get_vout(self):
        byte_data = self.get_serial_chunk()
        data_array = byte_data.decode('hex')
        vout_h = self.num_format(data_array[1].encode('hex'))
        vout_l = self.num_format(data_array[2].encode('hex'))

        # Caculate the Vout
        Vout = ((vout_h * 256) + vout_l) * 5 / 1024
        vout = round(Vout, 3)
        return vout

    def get_k(self, vout):

        """
        K represents a specific coefficient for the GP2Y1051AU0F dust sensor.
        The value of K will vary from the given value of Vout
        The conditions are searched from the internet, so it could be wrong.
        """
        if vout < 0.046:
            return 200
        if vout < 0.049:
            return 400
        if vout < 0.052:
            return 600
        if vout < 0.055:
            return 750
        if vout < 0.059:
            return 900
        if vout < 0.065:
            return 1000
        if vout < 0.071:
            return 1250
        if vout < 0.076:
            return 1400
        if vout < 0.081:
            return 1700
        if vout < 0.086:
            return 1800
        if vout < 0.091:
            return 1900
        if vout < 0.101:
            return 2000
        if vout < 0.111:
            return 2200
        else:
            return 3000

    def get_density(self):
        vout = self.get_vout()
        k = self.get_k(vout)

        # Dust density, unit: ug/m3
        dust_density = int(k * vout)
        return dust_density


if __name__ == '__main__':

    def show(aq):

        vout = aq.get_vout()
        density = aq.get_density()

        sys.stdout.write("[  Vout: %s V     |    Dust density: %s ug/m3 ] \r" % (vout, density))
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
            # print aq.get_serial_chunk()
            # print aq.get_vout()
            # print aq.get_density()
            time.sleep(1)
    except KeyboardInterrupt:
        ser.close()
        print "\nQuit!"
