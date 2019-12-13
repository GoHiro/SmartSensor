import RPi.GPIO as GPIO
from time import sleep
from DHT11_Python import dht11  # 温湿度センサーモジュール
import asyncio


class DevInfo:
    def __init__(self):
        self.serial_number = 'TempSensor C'
        self.function_name = 'RoomTemperatureMeasurement'


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


class TemperatureSendor:
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(host,
                                                       port,
                                                       loop=loop)
        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    def temp_sender(self, temperature):
        test_data = str(temperature)
        print('send value：' + test_data)
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

TEMP_SENSOR_PIN = 4  # 温湿度センサーのピンの番号
INTERVAL = 10  # 監視間隔（秒）
RETRY_TIME = 2  # dht11から値が取得できなかった時のリトライまので秒数
MAX_RETRY = 20  # dht11から温湿度が取得できなかった時の最大リトライ回数


class EnvSensorClass:  # 温湿度センサークラス
    def GetTemp(self):  # 温湿度を取得
        instance = dht11.DHT11(pin=TEMP_SENSOR_PIN)
        retry_count = 0
        while True:  # MAX_RETRY回まで繰り返す
            retry_count += 1
            result = instance.read()
            if result.is_valid():  # 取得できたら温度と湿度を返す
                return result.temperature, result.humidity
            elif retry_count >= MAX_RETRY:
                return 99.9, 99.9  # MAX_RETRYを過ぎても取得できなかった時に温湿度99.9を返す
            sleep(RETRY_TIME)

GPIO.setwarnings(False)  # GPIO.cleanup()をしなかった時のメッセージを非表示にする
GPIO.setmode(GPIO.BCM)  # ピンをGPIOの番号で指定

# main
try:
    if __name__ == "__main__":
        env = EnvSensorClass()
        temp = TemperatureSendor()
        while True:
            temperature, hum = env.GetTemp()  # 温湿度を取得
            send_data = data_insert_format(round(temperature))
            send_data = str(send_data)
            send_data = replace_reserved_strings(send_data)
            print(send_data)
            temp.temp_sender(send_data)
            print("温度 = ", temperature, " 湿度 = ", hum, "％")
            sleep(INTERVAL)
except KeyboardInterrupt:
    pass
GPIO.cleanup()