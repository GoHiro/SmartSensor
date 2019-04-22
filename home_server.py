from aiohttp import web
import asyncio
import json


class HomeServer:
    def __init__(self):
        self.received_data = 0
        self.smart_sensor_condition = 0
        self.smart_appliance_state = ''
        self.service_list = []


    # サービスの条件をチェックする。
    def check_condition(self, con, rec):
        print('条件:' + str(con) + '<= データ:' + str(rec))
        if con <= float(rec):
            print(float(rec))
            print('サービスを実行します（仮）')
            self.appliance_request()

    # HTTP通信ポートを定義する
        async def http_client(self, host, port, msg, loop):
            reader, writer = await asyncio.open_connection(
                host, port, loop=loop
            )
            writer.write(msg.encode())
            data = await reader.read()
            print(f'Received: {data.decode()}')
            writer.close()

    #
    #センサー
    #
    # センサーから受信データの中の式を指定して表示する。
    async def data_print(self, request):
        data = request.match_info.get('sensor_data', "Anonymous")
        print(data)
        self.received_data = data
        self.check_condition(self.smart_sensor_condition, data)
        return web.Response(text=data)

    def load_service(self, request):
        print('サービスを読み込み、条件の値を格納します。')
        with open('service.json', mode='r', encoding='utf-8') as f:
            data = json.load(f)
            self.service_list.append(data['service_name'])
            self.smart_sensor_condition = data['device_list'][0]['condition']
            self.smart_appliance_state = data['device_list'][1]['state']
            print(self.service_list)
            print("smart_sensor_condition = " + self.smart_sensor_condition)
            print("smart_appliance_state = " + self.smart_appliance_state)
            print('条件の値をセンサーへ送信します。')
            host = '127.0.0.1'
            port = 8020
            msg = (
                f'GET /sensor/get_condition HTTP/1.1 \r\n'
                'Host: localhost:8020\r\n'
                '\r\n'
                '\r\n'
            )

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.http_client(host, port, msg, loop))
            loop.close()
            return web.Response(text='ok')

    #
    #家電
    #
    # 家電へリクエストを送信する。
    def appliance_request(self):
        host = '127.0.0.1'
        port = 8030
        print('家電へAPIを送信します')
        msg = (
            f'GET /from/server HTTP/1.1\r\n'
            'Host: localhost:8000\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.http_client(host, port, msg, loop)
        loop.create_task(self.http_client(host, port, msg, loop))
        # loop.close()
        return web.Response(text='ok')


    # 受信したリクエストを表示する。
    async def msg_print(self, request):
        msg = request
        print(msg)
        return web.Response(text='ok')


    #
    #受信したリクエストを対応機能へルーティングする
    #
    def main(self):
        app = web.Application()
        # センサー
        app.router.add_get('/from/sensor', self.msg_print)
        app.router.add_get('/from/sensor/{sensor_data}', self.data_print)

        # 本機能
        app.router.add_get('/server/load_service', self.load_service)

        web.run_app(app, host='127.0.0.1', port=8010)


if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()