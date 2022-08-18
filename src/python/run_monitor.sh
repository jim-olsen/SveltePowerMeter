cd ./Documents/python/SveltePowerMeter/src/python/
python3 server.py &> monitor.out &
sleep 20
chromium-browser --start-fullscreen http://localhost:8050
