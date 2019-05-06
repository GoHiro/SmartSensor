import asyncio


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
        test_data = input()
        print('センサーへ入力する値：' + test_data)
        host = '127.0.0.1'
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
