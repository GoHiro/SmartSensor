import time
import RPi.GPIO as GPIO
import asyncio


class DevInfo:
    def __init__(self):
        self.serial_number = 'IRSensor C'
        self.function_name = 'DetectionStatus'


def data_insert_format(send_data):
  dev_info = DevInfo()
  send_data = "{" + f"'SerialNumber': '{dev_info.serial_number}'," \
              + "'Function': " + "{" + f"'FunctionName': '{dev_info.function_name}'," \
              + f"'Value': '{send_data}'" + "}}"
  return send_data

def replace_reserved_strings(res_str):
    # received data translate to original string
  reserved_to_unreserved = {'{': 'above_curly', ':': 'middle_colon',
                            '}': 'below_curly', "'": 'top_quote', ',': 'under_comma',
                            '@': 'attribute_at', '#': 'text_sharp', ' ': 'margin_space'}
  for reserved, unreserved in reserved_to_unreserved.items():
    res_str = res_str.replace(f'{reserved}', f'{unreserved}')
  return res_str


class DetectionSensor:
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(host,
                                                       port,
                                                       loop=loop)
        writer.write(msg.encode())
        data = await reader.read()
        print(f'Recieved: {data.decode()}')
        writer.close()

    def detection_sender(self, detection_status):
        test_data = str(detection_status)
        print('send value: ' + test_data)
        host = '169.254.137.173'
        port = 8020
        msg = (
            f'GET /sensor/test_data_create/{test_data} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()


SLEEP_TIME = 1
COOL_DOWN_TIME = 300
SENSOR_GPIO = 5


GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_GPIO, GPIO.IN)

if __name__ == '__main__':
    detection = DetectionSensor()
    while True:
        if GPIO.input(SENSOR_GPIO) == GPIO.HIGH:
            send_data = data_insert_format('True')
            send_data = str(send_data)
            send_data = replace_reserved_strings(send_data)
            print(send_data)
            detection.detection_sender(send_data)
            print('DetectionSensor: True')
            print(f'sleep_time: {COOL_DOWN_TIME}')
            time.sleep(COOL_DOWN_TIME)
        else:
            print('DetectionSensor: False')
        time.sleep(SLEEP_TIME)
GPIO.cleanup()
