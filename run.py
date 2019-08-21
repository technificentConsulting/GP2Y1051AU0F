from airq import airq
import serial

import random
import prometheus_client
from prometheus_client import Gauge
from flask import Response, Flask

# configure the serial connections (the parameters differs on the device you are connecting to)
# if uses Rpi serial port, the serial port login must be disable/stop first
# sudo systemctl stop serial-getty@ttyS0.service
ser = serial.Serial(
    port = 'COM8', # COM7 for windows
    baudrate = 2400,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

app = Flask(__name__)
dust_density_gauge = Gauge("dust_density", "dust density value of GP2Y1051AU0F")
vout_gauge = Gauge("vout", "Vout value")
k_gauge = Gauge("k", "k coefficient")

@app.route("/metrics")
def export_metrics():

    aq = airq.AIRQ(ser)

    data = aq.get_serial_chunk()
    vout = aq.get_vout(data)
    k    = aq.get_k(vout)

    dust_density = aq.get_density(vout)

    dust_density_gauge.set(dust_density)
    vout_gauge.set(vout)
    k_gauge.set(k)

    output = prometheus_client.generate_latest(dust_density_gauge)
    output += prometheus_client.generate_latest(vout_gauge)
    output += prometheus_client.generate_latest(k_gauge)

    return Response(output , mimetype="text/plain")

try:
    # print(export_metrics())
    app.run(host="0.0.0.0")
    # while 1:
        # aq.show()
        # debug()
        # print(get_serial_data())
        # time.sleep(1)

except KeyboardInterrupt:
    aq.ser.close()
