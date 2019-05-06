import asyncio


class ServiceConditionChecker:
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    def cron_check_service_condition(self):
        print('サーバへサービスの条件比較をリクエストします')
        host = '127.0.0.1'
        port = 8010
        msg = (
            f'GET /server/cron_check_service_condition HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()

    def main(self):
        # self.msg_test()
        self.cron_check_service_condition()


if __name__ == '__main__':
    service_c = ServiceConditionChecker()
    service_c.main()
