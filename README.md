Very basic web interface for serial data from cycle analyst. Dependencies is kept on bare minimum. Frameworks is absent on purpose.

Create .env file with

```
CA_HARDWARE_SERIAL=/dev/ttyS0 
PORT=8080
```

/dev/ttyS0 is UART of Raspberry Pi Zero 2 W

Raspberry Zero 2W has only one hardware uart. It is used for GNSS data due to higher baud rate
Cycle Analyst telemetry is read through software uart using pigpio


Install service
```bash
./install_service.sh
sudo systemctl enable pigpiod
```
Enable I2C and UART through raspi-config

Script for running commands
```bash
sudo cp bike.sh /usr/local/bin/bike
```

Than run
```bash
bike test_ads
```

### GNSS Setup on GL-X3000 Router
I use use this router for onboard network and internet. It also supports GNSS, which is enabled this way

Instruction from https://forum.gl-inet.com/t/howto-gl-x3000-gps-configuration-guide/30260
Internet -> Modem managemenet -> AT Command
```
AT+QGPSCFG="autogps",1
AT+QGPS=1
```
This should turn on GPS autostart whenever the router reboots, as well as start GPS acquisition right away.

#### Step 2: install and configure gpsd
Install gpsd via the Plugins page “Applications”

```bash
uci set gpsd.core.device='/dev/mhi_LOOPBACK'
uci set gpsd.core.listen_globally='1'
uci set gpsd.core.enabled='1'

/etc/init.d/gpsd enable
/etc/init.d/gpsd start
```
