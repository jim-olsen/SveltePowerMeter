cd ./Documents/python/SveltePowerMeter/src/python/
python3 server.py &> monitor.out &
sleep 10
chromium-browser --start-fullscreen http://localhost:8050
