import logging
import time
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO

from DFRobot_AS3935_Lib import DFRobot_AS3935

logger = logging.getLogger('energy_monitor')
# Set the address of the MQTT server to connect to for weather data and blue iris alerts
MQTT_SERVER_ADDR = '10.0.10.31'
MQTT_CLIENT: mqtt.Client = None
AS3935_I2C_ADDR = 0x03
AS3935_CAPACITANCE = 96
AS3935_IRQ_PIN = 4
LIGHTNING_SENSOR: DFRobot_AS3935 = None


#
# Startup the mqtt client and register callbacks to reconnect on any client disconnections
#
def start_mqtt_client():
    def on_connect(c, userdata, flags, rc):
        global MQTT_CLIENT

        logger.info("MQTT Client Connected")
        MQTT_CLIENT = c

    def on_disconnect(c, userdata, rc):
        logger.info(f"MQTT Client Disconnected due to {rc}, retrying....")
        while True:
            try:
                c.reconnect()
                break
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}, will retry....")
            time.sleep(30)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_SERVER_ADDR, 1883, 60)
    client.loop_forever()

def lightning_sensor_callback_handler(channel):
    global LIGHTNING_SENSOR, MQTT_CLIENT

    time.sleep(0.005)
    interrupt_source = LIGHTNING_SENSOR.get_interrupt_src()
    if interrupt_source == 1:
        logger.warning(f"Detected lightning at {LIGHTNING_SENSOR.get_lightning_distKm()}km and intensity  {LIGHTNING_SENSOR.get_strike_energy_raw()}")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'lightning',
                'distance': LIGHTNING_SENSOR.get_lightning_distKm(),
                'intensity': LIGHTNING_SENSOR.get_strike_energy_raw()
            }))
    elif interrupt_source == 2:
        logger.error("Lightning sensor detected a disturber")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'disturber'
            }))
    elif interrupt_source == 3:
        logger.error("Lightning sensor is detecting too much noise")
        if MQTT_CLIENT:
            MQTT_CLIENT.publish('lightning_data', json.dumps({
                'event': 'noise'
            }))


def main():
    global AS3935_IRQ_PIN, AS3935_CAPACITANCE, AS3935_I2C_ADDR, LIGHTNING_SENSOR

    logging.basicConfig()
    logging.getLogger('lightning detector').setLevel(logging.WARNING)

    logger.warning("Initializing AS3935")
    lightning_sensor = DFRobot_AS3935(AS3935_I2C_ADDR, bus=1)
    if lightning_sensor.reset():
        logger.warning("Lightning detector successfully initialized")
        lightning_sensor.power_up()
        lightning_sensor.set_outdoors()
        lightning_sensor.disturber_en()
        lightning_sensor.set_irq_output_source(0)
        time.sleep(0.5)
        lightning_sensor.set_tuning_caps(AS3935_CAPACITANCE)
        lightning_sensor.set_noise_floor_lv1(1)
        lightning_sensor.set_watchdog_threshold(2)
        lightning_sensor.set_spike_rejection(2)
        LIGHTNING_SENSOR = lightning_sensor
        GPIO.setup(AS3935_IRQ_PIN, GPIO.IN)
        GPIO.add_event_detect(AS3935_IRQ_PIN, GPIO.RISING, callback=lightning_sensor_callback_handler)
    else:
        logger.error("Lightning detector failed to initialize")

    start_mqtt_client()

if __name__ == "__main__":
    main()
