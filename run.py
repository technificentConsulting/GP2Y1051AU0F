from airq import airq
from prometheus_client import Gauge
from flask import Response, Flask
import serial
import prometheus_client
import configparser
import os

# configure the serial connections (the parameters differs on the device you are connecting to)
# if uses Rpi serial port, the serial port login must be disable/stop first
# sudo systemctl stop serial-getty@ttyS0.service

app = Flask(__name__)
dust_density_gauge = Gauge("dust_density", "dust density value of GP2Y1051AU0F")
vout_gauge = Gauge("vout", "Vout value")
k_gauge = Gauge("k", "k coefficient")

@app.route("/metrics")
def export_metrics():

    aq = airq.AIRQ()

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


# reads the configuration from settings file
config = configparser.ConfigParser()

dir_path = os.path.dirname(os.path.realpath(__file__))
settings_file_path = dir_path + '/settings.txt'
try:
    config.read(settings_files_path)
    server_ip   = config['server']['ip']
    server_port = config['server']['port']
except:
    print('Error! Please make sure that "settings.txt" file exists and properly set.')
    exit(1)

try:
    # print(export_metrics())
    
    app.run(host=server_ip, port=server_port)
    # while 1:
        # aq.show()
        # debug()
        # print(get_serial_data())
        # time.sleep(1)

except KeyboardInterrupt:
    aq.ser.close()
