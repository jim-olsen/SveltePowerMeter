cd ./SveltePowerMeter/src/python/
python3 server.py &> monitor.out &
sleep 20
chromium-browser --start-fullscreen --disable-session-crashed-bubble http://localhost:8050
