from aiohttp import web
import asyncio

# スマート家電サーバから受け取ったAPIに対応する機能を実行する


class SmartAppliance:
    """
    変数
    """
    def __init__(self):
        self.smart_appliance_power = 0

    # HTTP通信を行うための定義を行うメソッド
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    async def request_print(self, request):
        msg = request
        print(msg)
        return web.Response(text='ok')

    async def appliance_power_switch(self, request):
        appliance_power = request.match_info.get('appliance_power', "Anonymous")
        print(appliance_power)
        if appliance_power == 'off':
            self.smart_appliance_power = 0
        elif appliance_power == 'on':
            self.smart_appliance_power = 1
        else:
            print(self.smart_appliance_power)
        print('smart_appliance_power = ' + str(self.smart_appliance_power))
        return web.Response(text='appliance_power = ' + str(self.smart_appliance_power))

    def main(self):
        app = web.Application()
        app.router.add_get('/appliance/request_print', self.request_print)
        app.router.add_get('/appliance/appliance_power_switch/{appliance_power}', self.appliance_power_switch)
        web.run_app(app, host='127.0.0.1', port=8030)


if __name__ == '__main__':
    smart_appliance = SmartAppliance()
    smart_appliance.main()
