# GP2Y1051AU0F
Python script and Prometheus exporter for Sharp GP2Y1051AU0F Dust Sensor

## How does it work?
The device will keep sending 7 bytes serial data every 10ms.

### For example:

`AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF AA 00 02 00 61 63 FF ... ...`

The useful data chunk is formatted as `AA 00 02 00 61 63 FF` where `AA` represents the begining byte, `FF` represents the ending byte.

Second byte `00` is the Vout high **Vout(H)**, third byte `02` is the Vout low **Vout(L)**. The rest of the bytes will not be used.

### Caculation:

***Disclaimer: The the way of caculation is searched from the internet, it might be not correct***

`Vout = (Vout(H) * 256 + Vout(L)) / 1024 * 5`

*Vout(H) and Vout(L) need to be converted to decimal format first*

Given the data chunk `AA 00 02 00 61 63 FF`, we get:

Vout(H) = 00 in Hex = 0 in decimal

Vout(L) = 02 in Hex = 2 in decimal

So
`Vout = (0 * 256 + 2) / 1024 * 5 = 0.0097`

By using Vout, we can caculate the dust density with a coefficient **K** where K varies from the given Vout.

`Ud = K * Vout`

Where **Ud** represents the dust density (ug/m3)

if K = 200, then `Ud = 200 * 0.0097 = 1.94 (ug/m3)`

As to where to get the **K**, please look into the code.

|Vout|<0.045|0.046~0.048|0.049~0.051|0.052~0.054|0.055~0.058|0.059~0.064|0.065~0.07|
|---|---|---|---|---|---|---|---|
|K|200|400|600|750|900|1000|1250|
|Vout|0.071~0.075|0.076~0.080|0.081~0.085|0.086~0.090|0.091~0.1|0.101~0.11|>0.111|
|K|1400|1700|1800|1900|2000|2200|3000|

## Usage:
You can import this as the package or call it locally

### Local execute:
```
$ python airq/airq.py
````

### Run it with prometheus
if you execute the `run.py`, it will start a web engine with prometheus exporter on `https://0.0.0.0:5000/metrics`
