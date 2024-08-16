#!/bin/sh
if [ -z "$1" ]; then
    echo "Add command"
elif [ $1 = "update" ]; then
    cd /home/greyone/greybike/
    git pull
    cd /home/greyone/greybike/spa
    npm run build
    sudo systemctl restart greybike.service
elif [ $1 = "restart" ]; then
    sudo systemctl restart greybike.service
elif [ $1 = "stop" ]; then
    sudo systemctl stop greybike.service
else
    /home/greyone/greybike/.venv/bin/python /home/greyone/greybike/cli.py $1
fi
