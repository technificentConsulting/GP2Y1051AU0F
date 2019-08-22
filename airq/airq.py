#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import serial
import configparser

class AIRQ():
    """
    This program will read the data from Sharp GP2Y1051AU0F dust density sensor.
    The device will keep sending 1 byte serial data every 10ms.
    For example:
    AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63
    FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF ... ...

    The useful data chunk is formatted as:
    AA 00 02 00 61 63 FF

    Where AA represents the begining byte, FF represents the ending byte.
    Second byte 00 is the Vout high, third byte 02 is the Vout low
    """
    def __init__(self):

        # reads the configuration from settings file
        config = configparser.ConfigParser()

        try:
            config.read('settings.txt')
            self.serial_port = config['airq']['port']
            self.k = config['airq']['k']
        except:
            print('Error! Please make sure that "settings.txt" file exists and properly set.')
            exit(1)

        self.ser = serial.Serial(
            port = self.serial_port,
            baudrate = 2400,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1
        )

        # The device will keep sending 7 bytes data every 100ms
        self.serial_measure_bytes = 7

        # Read the chunk of the serial data, 2 times of the device output
        self.serial_expanded_measure_bytes = self.serial_measure_bytes * 2

    def get_serial_chunk(self):

        # read bytes from serial, we read the larger chunk(14 bytes) rather than 7 bytes.
        data = self.ser.read(self.serial_expanded_measure_bytes)

        self.ser.flush()
        
        # use all the rest of the data, we want to use the real time value
        #data += self.ser.readline(self.ser.inWaiting())

        if not data:
            return False

        try:
            # find out the first aa postion
            aa_index = data.index(b'\xaa')
        except ValueError:
            time.sleep(1)

        ## we will read 7 bytes in total
        ff_index = aa_index + self.serial_measure_bytes

        # Get the formmated chunk which start from AA, end with FF
        formatted_chunk = data[aa_index:ff_index]

        return formatted_chunk

    def num_format(self, num_hex):
        """
        Convert Hex value to decimal
        """
        num_int = int(num_hex)
        num_int = float(format(num_int, '.10f'))
        return num_int

    def get_vout(self, byte_data):
        # byte_data = self.get_serial_chunk()

        if not byte_data:
            return -1

        vout_h = self.num_format(byte_data[1])
        vout_l = self.num_format(byte_data[2])

        # print("VoutH: " + str(vout_h))
        # print("VoutL: " + str(vout_l))

        # Caculate the Vout
        # 0 - 5V mapped to 0 - 1023 integer values
        vout = ((vout_h * 256) + vout_l) * 5 / 1024
        # print(float(format(vout, '%.3f')))
        vout = round(vout, 4)
        return vout

    def get_k(self):

        """
        K represents a specific coefficient for the GP2Y1051AU0F dust sensor.
        The value of K may vary, since Sharp doesn't indicate any specific value.
        This K value is collected from the internet, so it might be not correct or accurate.
        Please set K value in settings.txt as you like.
        """
        return self.k

    def get_density(self, vout):

        k = self.get_k()

        # Dust density, unit: ug/m3
        density = float(k) * vout
        return density


if __name__ == '__main__':

    def show(aq):
        byte_data = aq.get_serial_chunk()
        vout = aq.get_vout(byte_data)
        # print("vout: " + str(vout))
        if not byte_data:
            print("Waiting for serial data...")

        # print("line: " + chunk)
        # print("in_waiting: " + str(aq.ser.in_waiting) + " byte(s)")

        k = aq.get_k()
        density = aq.get_density(vout)

        sys.stdout.write("[ %s | K: %s | Vout: %5.4f V | Dust density: %5.2f ug/m3 ] \r" % ( byte_data.hex(), k, vout, density))
        sys.stdout.flush()
        time.sleep(1)

    try:

        aq = AIRQ()
        while 1:
            show(aq)
            # data = aq.get_serial_chunk()
            # vout = aq.get_vout()
            # density = aq.get_density(vout)
            # if data:
            #     print(data)
            #     print(vout)
            #     print(density)
            #     time.sleep(1)
            # else:
            #     print("waiting for serial data")
    except KeyboardInterrupt:
        aq.ser.close()
        print("\nQuit!")
