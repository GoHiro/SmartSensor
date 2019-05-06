from aiohttp import web
import asyncio
import json


class HomeServer:
    # サーバとセンサ、家電で同期している変数を保持する
    def __init__(self):
        self.get_data = 0
        self.smart_sensor_port = 0
        self.smart_sensor_condition = 0
        self.smart_appliance_port = 0
        self.smart_appliance_power = ''
        self.service = []

    # HTTP通信を行うための定義を行うメソッド
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    # サービスの内容を変数に置き換え
    async def load_service(self, request):
        print('サービスを読み込み、条件の値を読み込む')
        with open('service.json', mode='r', encoding='utf-8') as f:
            data = json.load(f)
            self.service.append(data['service_name'])
            self.smart_sensor_port = int(data['device_list'][0]['port'])
            self.smart_sensor_condition = int(data['device_list'][0]['condition'])
            self.smart_appliance_port = int(data['device_list'][1]['port'])
            self.smart_appliance_power = data['device_list'][1]['state']
            print(self.service)
            print("smart_sensor_condition = " + str(self.smart_sensor_condition))
            print("smart_appliance_state = " + self.smart_appliance_power)
            await self.set_condition()

    # センサーへself.sensor_conditionを送信する
    async def set_condition(self):
        print('センサーへ条件の登録を行います')
        host = '127.0.0.1'
        port = self.smart_sensor_port
        sensor_condition = self.smart_sensor_condition
        msg = (
            f'GET /sensor/set_condition/{sensor_condition} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        # loop.create_task(self.http_client(host, port, msg, loop))
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()
        return web.Response(text='ok')

    # request内部の式'sensor_data'から受信データを取り出す
    async def get_sensor_data(self, request):
        get_data = request.match_info.get('sensor_data', "Anonymous")
        print(get_data)
        self.get_data = int(get_data)
        await self.check_service_condition()
        return web.Response(text='ok')

    # self.smart_sensor_conditionとself.received_dataを比較する
    async def check_service_condition(self):
        print('条件:' + str(self.smart_sensor_condition) + '<= データ:' + str(self.get_data))
        if self.smart_sensor_condition <= self.get_data:
            print(float(self.get_data))
            print('条件を満たしました、サービスを実行します')
            await self.appliance_power_switch()
        else:
            print('条件を満たしていません')

    # cronで一定時間ごとにサービスの条件を比較する
    async def cron_check_service_condition(self, request):
        print('条件:' + str(self.smart_sensor_condition) + '<= データ:' + str(self.get_data))
        if self.smart_sensor_condition <= self.get_data:
            print(float(self.get_data))
            print('条件を満たしました、サービスを実行します')
            await self.appliance_power_switch()
        else:
            print('条件を満たしていません')

    # 家電へリクエストを送信する。
    async def appliance_power_switch(self):
        host = '127.0.0.1'
        port = self.smart_appliance_port
        appliance_power = self.smart_appliance_power
        print('家電へAPIを送信します')
        msg = (
            f'GET /appliance/appliance_power_switch/{appliance_power} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.create_task(self.http_client(host, port, msg, loop))
        # loop.run_until_complete(self.http_client(host, port, msg, loop)
        # loop.close()
        return web.Response(text='ok')

    # 受信したmsgの'request'を表示する。
    async def msg_test(self, request):
        msg = 'test'
        print(msg)
        print(request)
        return web.Response(text='ok')

    # msgと同名のメソッドへへルーティングする
    def main(self):
        app = web.Application()

        # センサーとの通信を含む
        app.router.add_get('/server/get_sensor_data/{sensor_data}', self.get_sensor_data)

        # サーバー内部を参照する
        app.router.add_get('/server/msg_test', self.msg_test)
        app.router.add_get('/server/load_service', self.load_service)
        app.router.add_get('/server/cron_check_service_condition', self.cron_check_service_condition)

        # 家電との通信を含む
        # app.router.add_get('/appliance/',self.)

        web.run_app(app, host='127.0.0.1', port=8010)


if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()
