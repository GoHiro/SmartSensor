from aiohttp import web
import asyncio
import json

import csv
import serial
from struct import *
from binascii import *
import time
import random



class HomeServer:
    # サーバとセンサ、家電で同期している変数を保持する
    def __init__(self):
        self.get_data = 0
        self.smart_sensor_port = 0
        self.smart_sensor_condition = 0
        self.smart_appliance_port = 0
        self.smart_appliance_power = ''
        self.service = []

        self.kaden = 0
        self.state = 0
        self.channel = 0
        self.temp = 0
        self.rtemp = 0
        self.vol = 0
        self.time = 0
        self.settei = 0
        self.dict = {}

        # csv
        self.f = open('data.csv', 'r')
        self.reader = csv.reader(self.f)
        for row in self.reader:
            self.l_value = [row[1], row[2], row[3]]  # 学習リモコンの on/off の 値も読み込めるようにする
            self.dict.update({row[0]: self.l_value})
            print(self.dict)
        ###
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 3)
        self._LED = pack('B', 0x69)  # LED 点灯
        self._RECEIVE = pack('B', 0x72)  # 送信
        self._TRANSMIT = pack('B', 0x74)  # 受信
        self.ch1 = pack('B', 0x31)  # A の黄
        self.ch2 = pack('B', 0x32)  # A の黒
        self.ch3 = pack('B', 0x33)  # B の黄
        self.ch4 = pack('B', 0x34)  # B の黒
        self.r_data = 0  # 受信する際の変数

    # csv
    def diction(self, value):
        print(self.dict[str(value)])  # 確認

        self.change_name(self.dict[str(value)][0])
        # 辞書値であるリストの 0 番目要素の取り出し
        self.change_state(self.dict[str(value)][1])
        # 辞書地であるリストの 1 番目の要素の取り出し
        # ここに学習リモコンに送る信号命令を書けばいい(※信号の文字列判別を行う必要はない)
        print(self.ch1)
        print(self.dict[str(value)][2])
        self.transmit(self.dict[str(value)][2], self.ch1)

    def change_name(self, name):
        data = str(name)

        print(str(data))
        self.kaden = data

    def change_state(self, kaden_state):
        data = str(kaden_state)

        print(str(data))
        self.state = data

    def change_settei(self, k_settei):
        data = str(' ' + k_settei)

        self.settei = data

    def change_channel(self, c_settei):
        data = str(' ' + c_settei)
        self.channel = data

    def change_temp(self, t_settei):
        data = str(' ' + t_settei)
        self.temp = data

    def change_vol(self, v_settei):
        data = str(' ' + v_settei)
        self.vol = data

    def change_time(self, tm_settei):
        data = str(' ' + tm_settei)
        self.time = data

    def change_roomtemp(self, troom_settei):  # 外部機器から温度が送られてきたとき使用
        data = str(' ' + troom_settei)
        self.rtemp = data

    def led(self):
        """LED を点灯させる"""
        self.ser.write(self._LED)
        self.ser.read()  # 0x4f

    def receive(self) -> bytes:
        """赤外線を受信する"""
        print('receiving...' + str(self.r_data))
        self.ser.write(self._RECEIVE)
        self.ser.read(1)  # 0x59
        self.ser.read(1)  # 0x53
        self.r_data = hexlify(self.ser.read(240))  # このデータを送信(リモコンで何かしらの信号送信)
        self.ser.read(1)
        print('received:' + str(self.r_data))  # 0x45
        return self.r_data

    def transmit(self, hex_data: bytes, channel: bytes):
        """ 赤外線を送信する"""
        bin_data = a2b_hex(hex_data)
        self.ser.write(self._TRANSMIT)
        self.ser.read(1)  # 0x59
        self.ser.write(channel)  # チャンネルの指定
        self.ser.read(1)  # 0x59
        self.ser.write(bin_data)  # データの送信
        self.ser.read(1)  # 0x45

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.ser.close()

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

    async def handle_poll(self, request):
        text = "kaden " + str(self.kaden) + "¥n"
        text2 = "state " + str(self.state) + "¥n"
        text3 = "chanel " + str(self.chanel) + "¥n"
        text4 = "temp " + str(self.temp) + "¥n"
        text5 = "vol " + str(self.vol) + "¥n"
        text6 = "time " + str(self.time) + "¥n"
        text7 = "roomtemp " + str(random.randint(10, 30)) + "¥n"
        text8 = "humansensa " + str(random.randint(0, 1)) + "¥n"
        text9 = "lightsensa " + str(random.randint(0, 1)) + "¥n"
        return web.Response(text=text + text2 + text3 + text4 + text5 + text6 + text7 + text8 + text9)

    async def handle_poll2(self, request):
        text7 = "roomtemp" + str(self.rtemp) + "¥n"
        return web.Response(text=text7)

    async def handle_broadcast(self, request):
        kadenname = request.match_info['buff1']  # 値の受け取り
        print(type(kadenname))
        print("Scratch から受け取った値 : " + "a" + str(kadenname) + "a")  # 受け取った値の出力1
        self.diction(kadenname)
        return web.Response(text="OK")

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
        app.router.add_get('/event_broadcast/{buff1}',self.handle_broadcast)    # buffにはテレビとかが入る
        # LEDを点灯
        self.led()
        self.receive()

        web.run_app(app, host='127.0.0.1', port=8010)


if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()
