import asyncio


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



class DevInfo:
    def __init__(self):
        """define sendig message here"""
        self.serial_number = 'TempSensor C'
        self.function_name = 'TemperatureMeasurementValue'
        self.value = '2'

class SensorController:
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    def test_data_create(self):
        dev_info = DevInfo()
        test_data = dev_info.value
        test_data = data_insert_format(test_data)
        print(test_data)
        test_data = replace_reserved_strings(test_data)
        print('センサーへ入力する値：' + test_data)
        host = '169.254.137.173'
        port = 8020
        msg = (
            f'GET /sensor/test_data_create/{test_data} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()

    def main(self):
        self.test_data_create()


if __name__ == '__main__':
    sensor_c = SensorController()
    sensor_c.main()
