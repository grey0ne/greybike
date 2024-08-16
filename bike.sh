#!/bin/sh
if [ $1 = "update" ]; then
    cd /home/greyone/greybike/
    git pull
    cd /home/greyone/greybike/spa
    npm run build
    sudo systemctl restart greybike.service
else
    /home/greyone/greybike/.venv/bin/python /home/greyone/greybike/cli.py $1
fi
