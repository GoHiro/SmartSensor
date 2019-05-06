from aiohttp import web
import random
import asyncio


class SmartSensor:
    def __init__(self):
        # self.appliance_state = 0
        self.test_data = 0
        self.sensor_condition = 999

    # HTTP通信のポート定義
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    # 外部との通信
    # サービスの条件をリクエスト
    #def get_condition(self,request):
    #    host = '127.0.0.1'
    #    port = 8010
    #    print('条件を取得します。')
    #    msg = (
    #        f'GET /from/sensor/get HTTP/1.1\r\n'
    #        'Host: localhost:8010\r\n'
    #        '\r\n'
    #        '\r\n'
    #    )
    #    loop = asyncio.get_event_loop()
    #    loop.run_until_complete(self.http_client(host, port, msg, loop))
    #    loop.close()

    # センサの条件をセット
    async def set_condition(self, request):
        print('サービスの条件をセットする')
        data = request.match_info.get('sensor_condition', "Anonymous")
        self.sensor_condition = int(data)
        print("現在の条件：" + str(self.sensor_condition))
        return web.Response(text='ok')

    # テストデータ生成
    async def test_data_create(self, request):
        # self.sensor_data = (random.uniform(10, 30))
        # self.sensor_data = round(self.sensor_data, 1)
        print('入力した値を犬種した値として扱うテスト')
        test_data = request.match_info.get('test_data', "Anonymous")
        self.test_data = int(test_data)
        print('test_data='+str(test_data))
        if self.test_data >= self.sensor_condition:
            await self.get_sensor_data()
        else:
            print('条件を満たしていません')
        return web.Response(text='ok')

    # 条件を満たしたデータをサーバへ送信する
    async def get_sensor_data(self):
        host = '127.0.0.1'
        port = 8010
        print('条件を満たしました。通知を行います。')
        sensor_data = self.test_data
        msg = (
            f'GET /server/get_sensor_data/{sensor_data} HTTP/1.1\r\n'
            'Host: localhost:8020\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()  # get_loop
        loop.run_until_complete(self.http_client(host, port, msg, loop))  # until_get_complete
        loop.close()

    def main(self):
        app = web.Application()

        app.router.add_get('/sensor/set_condition/{sensor_condition}', self.set_condition)
        app.router.add_get('/sensor/test_data_create/{test_data}', self.test_data_create)

        web.run_app(app, host='127.0.0.1', port=8020)


if __name__ == '__main__':
    smart_sensor = SmartSensor()
    smart_sensor.main()
