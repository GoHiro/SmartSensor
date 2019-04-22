from aiohttp import web
import random
import asyncio


class SmartSensor:
    def __init__(self):
        # self.appliance_state = 0
        self.sensor_data = 0
        self.push_condition = 500

    #条件データの格納
    def condition_set(self):
        print('受け取ったデータを条件にセットします。')
        print('現在の条件：')

    # センサーデータ生成
    def data_create(self):
        self.sensor_data = (random.uniform(10, 30))
        self.sensor_data = round(self.sensor_data, 1)
        return self.sensor_data

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
    # サーバから条件となる値を格納する
    def get_condition(self,request):
        host = '127.0.0.1'
        port = 8010
        print('条件を取得します。')
        msg = (
            f'GET /from/sensor/get HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()

    # 条件を満たしたデータをサーバへ送信する
    def push_data(self):
        host = '127.0.0.1'
        port = 8010
        print('指定した条件を満たしました。通知を行います。')
        sensor_data = self.sensor_data
        msg = (
            f'GET /from/sensor/{sensor_data} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()  # get_loop
        loop.run_until_complete(self.http_client(host, port, msg, loop))  # until_get_complete
        loop.close()


    def main(self):
        """
        app = web.Application()
        app.router.add_get('/appliance/power/on', self.#ここに条件設定クラス)    # state:1

        web.run_app(app, host='127.0.0.1', port=8020)          # port_set
        """
        # 起動時に、条件をサーバから取得
        #self.get_condition()

        data = self.data_create()
        print(data)
        if data >= 24:
            self.push_data()


if __name__ == '__main__':
    smart_sensor = SmartSensor()
    smart_sensor.main()
