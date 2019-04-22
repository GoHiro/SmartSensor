import asyncio


class SensorDataSet:
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()


    def create_data(self):
        data = 0
        print('センサーへ送る値を入力(0~99)')
        data = input()
        print('センサーへ入力する値：' + data)
        host = '127.0.0.1'
        port = 8010
        msg = (
            f'GET /server/load_service HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()


    def main(self):
        print(1)
        self.create_data()

if __name__ == '__main__':
    dataset = SensorDataSet()
    dataset.main()
