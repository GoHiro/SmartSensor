from aiohttp import web
import random
import asyncio
import ast
from pprint import pprint


async def get_data_of_specified_key(target_data: object, key_to_target_data: object) -> object:
    for key in key_to_target_data:
        target_data = target_data[key]

    return target_data


async def replace_reserved_strings(res_str):
    reserved_to_unreserved = {'{': 'above_curly', ':': 'middle_colon',
                              '}': 'below_curly', "'": 'top_quote', ',': 'under_comma',
                              '@': 'attribute_at', '#': 'text_sharp', ' ': 'margin_space',
                              '[': 'above_list', ']': 'below_list'}
    for reserved, unreserved in reserved_to_unreserved.items():
        res_str = res_str.replace(f'{reserved}', f'{unreserved}')
    return res_str


async def replace_previous_string(res_str):
    # original string replaces to usable string on arrangement of http
    unreserved_to_previous_string = {'above_curly': '{', 'middle_colon': ':',
                                     'below_curly': '}', 'top_quote': "'", 'under_comma': ',',
                                     'attribute_at': '@', 'text_sharp': '#', 'margin_space': ' ',
                                     'above_list': '[', 'below_list': ']'}
    for unreserved, previous in unreserved_to_previous_string.items():
        res_str = res_str.replace(f'{unreserved}', f'{previous}')
    return res_str


class SmartSensor:
    def __init__(self):
        # self.sensor_condition = 999
        self.create_table_flag = 0
        self.recv_data = {}
        self.condition_dict = {}
        self.key_to_value = [0, 'ns2:Value']
        self.target_dict = ''
        self.target_function = ''
        self.latest_sensor_list = []

    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    async def judge_value_type(self, value_type):
        if value_type == 'equal':
            judged_type = '=='
        elif value_type == 'upper':
            judged_type = '>='
        elif value_type == 'lower':
            judged_type = '<'
        else:
            print('no matched type')
            judged_type = 0

        return judged_type

    async def judge_value_text(self, value_text):
        if value_text == 'TRUE':
            judged_value = 'True'
        elif value_text == 'FALSE':
            judged_value = 'False'
        else:
            judged_value = value_text

        return judged_value

    async def stand_table_flag(self):
        self.create_table_flag = 1

    async def check_table_flag(self):
        if self.create_table_flag == 0:
            return True
        else:
            return False

    async def create_notification_table(self, table_name, table_function, table_value):
        concatenate_dict = + f"['{table_value}']"

        return concatenate_dict

    async def set_condition(self, request):
        data = request.match_info.get('sensor_condition', "Anonymous")
        recv_data = await replace_previous_string(data)
        recv_data = ast.literal_eval(recv_data)
        for part_of_recv_data in recv_data:
            self.recv_data = part_of_recv_data
            print('recv_data')
            print(self.recv_data)
            self.recv_data = self.recv_data['packed_condition']
            print('recv_data')
            pprint(self.recv_data)
            print('condition_dict')
            pprint(self.condition_dict)
            if self.condition_dict == {}:
                self.condition_dict = self.recv_data
                print('condition_dict')
                pprint(self.condition_dict)
                print(type(self.condition_dict))
            await self.is_serial_function_existance()
            await self.check_type_of_recv_data()
            await self.is_value_list_existance()
            print('<condition_dict>')
            pprint(self.condition_dict)
        return web.Response(text='ok')

    async def check_type_of_recv_data(self):
        test_dict = [{'test': 'text'},{'test2': 'text2'}]
        assert type(self.condition_dict) == type(test_dict), f'assert error text: {self.condition_dict}'

    async def set_dict_count(self, current_num):
        self.key_to_value = [current_num , "ns2:Value"]

    async def is_serial_function_existance(self):

        for recv_data in self.recv_data:
            serial_function_flag = False
            for condition_dict in self.condition_dict:
                if recv_data['ns2:SerialNumber'] == condition_dict['ns2:SerialNumber'] and \
                    recv_data['pc:FunctionName'] == condition_dict['pc:FunctionName']:
                    serial_function_flag = True
            if not serial_function_flag:
                self.condition_dict.append(recv_data)


    async def is_value_list_existance(self):
        dict_count = len(self.recv_data)
        condition_count = len(self.condition_dict)
        for current_num in range(dict_count):
            await self.set_dict_count(current_num)
            print('-condition_dict-')
            pprint(self.condition_dict)
            pprint(self.recv_data)
            print(f'dict_count: {dict_count}')
            print(self.key_to_value)
            judge_dict = await get_data_of_specified_key(self.condition_dict,
                                                         self.key_to_value)

            print(f'judge_dict: {judge_dict}')
            print(type(judge_dict))
            for condition_num in range(condition_count):
                if 'ValueList' not in judge_dict:
                    await self.insert_value_list(current_num, condition_num)
                elif 'ValueList' in judge_dict:
                    await self.append_value_list(current_num, condition_num)

    async def insert_value_list(self, current_num, condition_num):
        print('insert value_list')
        if self.recv_data[current_num]["pc:FunctionName"] == \
            self.condition_dict[condition_num]["pc:FunctionName"]:
            value_dict = await get_data_of_specified_key(self.recv_data,
                                                     self.key_to_value)
            insert_value = await self.translate_to_value(value_dict)
            self.condition_dict[condition_num]['ns2:Value']['ValueList'] = [insert_value]
            print(self.condition_dict[condition_num]['ns2:Value']['ValueList'])
            print(type(self.condition_dict[condition_num]['ns2:Value']['ValueList']))

    async def append_value_list(self, current_num, condition_num):
        print('append value_list')
        # fixme: value_dict is find in condition_dict, not recv_data
        if self.recv_data[current_num]["pc:FunctionName"] == \
                self.condition_dict[condition_num]["pc:FunctionName"]:
            value_dict = await get_data_of_specified_key(self.recv_data,
                                                     self.key_to_value)
            await self.check_current_struct()
            append_value = await self.translate_to_value(value_dict)
            if append_value not in self.condition_dict[condition_num]['ns2:Value']['ValueList']:
                self.condition_dict[condition_num]['ns2:Value']['ValueList'].append(append_value)
                print(self.condition_dict[condition_num]['ns2:Value']['ValueList'])
                print(type(self.condition_dict[condition_num]['ns2:Value']['ValueList']))
            elif append_value in self.condition_dict[condition_num]['ns2:Value']['ValueList']:
                print('already contain')

    async def check_current_struct(self):
        print('recv_data')
        print(self.recv_data)
        print('condition_dict')
        print(self.condition_dict)

    async def translate_to_value(self, value_dict):
        value_type = value_dict['@type']
        value_type = await self.judge_value_type(value_type)
        value_text = value_dict['#text']
        value_text = await self.judge_value_text(value_text)
        translate_value = value_type + value_text
        print(translate_value)  # ==True

        return translate_value

    async def create_test_data(self, request):
        # please compare sensor_data with adapted condition
        # if matched data found, matched data send back to homeserver
        sensor_data = request.match_info.get('test_data', "Anonymous")
        sensor_data = await replace_previous_string(sensor_data)
        sensor_data = ast.literal_eval(sensor_data)
        print(f'sensor_data: {sensor_data}')
        self.sensor_dict = sensor_data
        await self.check_existence_sensor_data(sensor_data)
        await self.search_same_value()
        return web.Response(text='ok')

    async def check_existence_sensor_data(self, sensor_data):
        not_append_flag = False
        if not self.latest_sensor_list:
            await self.append_sensor_data_forming(sensor_data)
        else:
            for latest_sensor_data in self.latest_sensor_list:
                if latest_sensor_data.get(sensor_data['SerialNumber']):
                    if latest_sensor_data[sensor_data['SerialNumber']].get(sensor_data['Function']['FunctionName']):
                        not_append_flag = True
            if not not_append_flag:
                await self.append_sensor_data_forming(sensor_data)

    async def append_sensor_data_forming(self, sensor_data):
        append_serial = sensor_data['SerialNumber']
        append_function_name = sensor_data['Function']['FunctionName']
        append_value = sensor_data['Function']['Value']
        append_data = {append_serial: {append_function_name: append_value}}
        await self.add_append_sensor_data(append_data)

    async def add_append_sensor_data(self, append_data):
        print(f'append_data: {append_data}')
        self.latest_sensor_list.append(append_data)
        print(f'latest_sensor_list: {self.latest_sensor_list}')

    async def search_same_value(self):
        # sensor_data = ['IRSensor C', 'DetectionStatus', 'True']
        await self.key_check_at_device_and_function(self.sensor_dict, self.condition_dict)
        print('self.sensor_dict')
        print(self.sensor_dict)
        print('self.condition_dict')
        print(self.condition_dict)
        for condition in self.condition_dict:
            print('condition')
            print(type(condition))
            print(condition)
            if condition['ns2:SerialNumber'] == self.sensor_dict['SerialNumber'] and \
                condition['pc:FunctionName'] == self.sensor_dict['Function']['FunctionName']:
                key_to_value_list = ['ns2:Value', 'ValueList']
                value_list = await get_data_of_specified_key(condition, key_to_value_list)

    async def key_check_at_device_and_function(self, sensor, condition):
        serial_number_in_sensor = sensor['SerialNumber']
        function_name_in_sensor = sensor['Function']['FunctionName']
        for part_of_condition in condition:
            key_to_serial_number_in_condition = ['ns2:SerialNumber']
            key_to_function_name_in_condition = ['pc:FunctionName']
            serial_number_in_condition = await get_data_of_specified_key(part_of_condition, key_to_serial_number_in_condition)
            function_name_in_condition = await get_data_of_specified_key(part_of_condition, key_to_function_name_in_condition)

            if serial_number_in_sensor == serial_number_in_condition and function_name_in_sensor == function_name_in_condition:
                await self.eval_condition_strings(part_of_condition)

    async def eval_condition_strings(self, part_of_condition):
        key_to_value_in_sensor = ['Function', 'Value']
        key_to_value_in_condition = ['ns2:Value', 'ValueList']
        sensor_value = await get_data_of_specified_key(self.sensor_dict,
                                                 key_to_value_in_sensor)
        value_list = await get_data_of_specified_key(part_of_condition,
                                               key_to_value_in_condition)
        for value in value_list:
            str = sensor_value + value
            if eval(str):
                key_to_serial_number_in_sensor = ['SerialNumber']
                key_to_function_name_in_sensor = ['Function', 'FunctionName']
                serial_number = await get_data_of_specified_key(self.sensor_dict,
                                                          key_to_serial_number_in_sensor)
                function_name = await get_data_of_specified_key(self.sensor_dict,
                                                          key_to_function_name_in_sensor)
                sensor_data = {'SerialNumber': f'{serial_number}',
                               'FunctionName': f'{function_name}',
                               'Value': f'{sensor_value}'}
                print(f'sensor_data: {sensor_data}')
                await self.get_sensor_data(sensor_data)
                break
            else:
                print('data does not match...')

    async def get_sensor_data(self, sensor_data):
        host = '169.254.12.61'
        port = 8010
        print('条件を満たしました。通知を行います。')
        sensor_data = await replace_reserved_strings(str(sensor_data))
        print(sensor_data)
        msg = (
            f'GET /server/get_sensor_data/{sensor_data} HTTP/1.1\r\n'
            'Host: localhost:8020\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_running_loop()  # get_loop
        loop.create_task(self.http_client(host, port, msg, loop))  # until_get_complete


    async def send_latest_value_list(self):
        host = '169.254.12.61'
        port = 8010
        print('条件を満たしました。通知を行います。')
        sensor_data = await replace_reserved_strings(str(self.latest_sensor_list))
        print(self.latest_sensor_list)
        msg = (
            f'GET /server/sensor_value_for_after_condition/{sensor_data} HTTP/1.1\r\n'
            'Host: localhost:8020\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_running_loop()  # get_loop
        loop.create_task(self.http_client(host, port, msg, loop))  # until_get_complete


    """
    condition_dict translate 
    equal -> '==' , upper -> '>=' , lower -> <'
    measured_data = 25
    {measered_data} + '>=23'

    value = 23
    type = 'upper'
    if type == 'upper':
        expression = '>' + f'{value}'
    expressioncheck_tipy
    '>23'
    measured_value = 25
    compare_expression = f'{measured_value}' + f'{expression}'
    eval(compare_expression)
    True"""

    async def get_current_sensor_value_from_smart_sensor(self, request):
        if self.send_latest_value_list:
            await self.send_latest_value_list()

    def main(self):
        print('Starting Smart Sensor...')
        app = web.Application()
        app.router.add_get('/sensor/set_condition/{sensor_condition}', self.set_condition)

        app.router.add_get('/sensor/test_data_create/{test_data}', self.create_test_data)
        app.router.add_get('/sensor/get_current_sensor_value_from_smart_sensor', self.get_current_sensor_value_from_smart_sensor)
        web.run_app(app, host='169.254.137.173', port=8020)


if __name__ == '__main__':
    smart_sensor = SmartSensor()
    smart_sensor.main()
