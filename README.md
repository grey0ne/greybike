Very basic web interface for serial data from cycle analyst. Dependencies is kept on bare minimum. Frameworks is absent on purpose.

Create .env file with

```
CA_SERIAL=/dev/ttyS0 
PORT=8080
```

/dev/ttyS0 is UART of Raspberry Pi Zero 2 W

Run
```bash
./run.sh
```

Install service
```bash
./install_service.sh
```

Download external JS
```bash
./update_js.sh
```
