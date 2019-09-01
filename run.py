from airq import airq
from prometheus_client import Gauge
from flask import Response, Flask
import serial
import prometheus_client
import configparser
import os

"""
# configure the serial connections (the parameters differs on the device you are connecting to)
# if you use Raspberry pi serial port, the serial port login must be disable/stop prior to use it.
# Use "raspi-config" to turn of serial console, or run the following command:
# sudo systemctl stop serial-getty@ttyS0.service
"""

aq = airq.AIRQ()

app = Flask(__name__)
dust_density_gauge = Gauge("dust_density", "dust density value of GP2Y1051AU0F")
vout_gauge = Gauge("vout", "Vout value")
k_gauge = Gauge("k", "k coefficient")

@app.route("/metrics")
def export_metrics():

    data = aq.get_serial_chunk()
    vout = aq.get_vout(data)
    k    = aq.get_k()

    dust_density = aq.get_density(vout)

    dust_density_gauge.set(dust_density)
    vout_gauge.set(vout)
    k_gauge.set(k)

    output = prometheus_client.generate_latest(dust_density_gauge)
    output += prometheus_client.generate_latest(vout_gauge)
    output += prometheus_client.generate_latest(k_gauge)

    return Response(output , mimetype="text/plain")

try:

    server_ip = aq.config['server']['ip']
    server_port = aq.config['server']['port']
    app.run(host=server_ip, port=server_port)
    # while 1:
        # aq.show()
        # debug()
        # print(get_serial_data())
        # time.sleep(1)

except KeyboardInterrupt:
    aq.ser.close()
