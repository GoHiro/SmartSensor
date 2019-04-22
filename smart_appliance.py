from aiohttp import web
import asyncio

# スマート家電サーバから受け取ったAPIに対応する機能を実行する


class SmartAppliance:
    """
    変数
    """
    def __init__(self):
        self.appliance_power = 0

    async def request_print(self, request):
        msg = request
        print(msg)
        return web.Response(text='ok')

    async def power_switch(self, request):
        data = request.match_info.get('power_state', "Anonymous")
        print(data)
        if int(data) == 0:
            self.appliance_power = 0
        elif int(data) == 1:
            self.appliance_power = 1
        else:
            print(self.appliance_power)
        return web.Response(text='appliance_power = ' + str(self.appliance_power))

    def main(self):
        app = web.Application()
        app.router.add_get('/from/server', self.request_print)
        app.router.add_get('/from/server/power/{power_state}', self.power_switch)
        web.run_app(app, host='127.0.0.1', port=8030)


if __name__ == '__main__':
    smart_appliance = SmartAppliance()
    smart_appliance.main()
