Very basic web interface for serial data from cycle analyst. Dependencies is kept on bare minimum. Frameworks is absent on purpose.

Create .env file with

```
SERIAL=/dev/ttyS0 
PORT=8080
```

/dev/ttyS0 is UART of Raspberry Pi Zero 2 W

Run
./run.sh

Install service
./install_service.sh
