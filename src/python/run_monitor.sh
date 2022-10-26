cd /home/clifwlkr/SveltePowerMeter/src/python/
python3 server.py &> monitor.out &
sleep 20
#chromium-browser --start-fullscreen --disable-session-crashed-bubble http://localhost:8050
chromium-browser --kiosk --app-auto-launched --disk-cache-dir=/dev/null --disk-cache-size=1 --app=http://localhost:8050