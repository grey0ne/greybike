python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
sudo cp greybike.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/greybike.service
sudo systemctl daemon-reload
sudo systemctl enable greybike.service
sudo systemctl start greybike.service
