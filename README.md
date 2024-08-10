Very basic web interface for serial data from cycle analyst. Dependencies is kept on bare minimum. Frameworks is absent on purpose.

Create .env file with

```
CA_SERIAL=/dev/ttyS0 
PORT=8080
```

/dev/ttyS0 is UART of Raspberry Pi Zero 2 W

Raspberry Zero 2W has only one hardware uart. It is used for GNSS data due to higher baud rate
Cycle Analyst telemetry is read through software uart using pigpio

Run
```bash
./run.sh
```

Install service
```bash
./install_service.sh
```


