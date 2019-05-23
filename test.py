import myserial
from struct import *
from binascii import *
import traceback
import sys


class PC_OP_RS1():

    def __init__(self):
        self._LED      = pack('B', 0x69) # LED点灯
        self._RECEIVE  = pack('B', 0x72) # 送信
        self._TRANSMIT = pack('B', 0x74) # 受信
        self.ch1 = pack('B', 0x31)       # Aの黄
        self.ch2 = pack('B', 0x32)       # Aの黒
        self.ch3 = pack('B', 0x33)       # Bの黄
        self.ch4 = pack('B', 0x34)       # Bの黒

    def connect(self, com):
        u"""
        portに接続する
        :param int com:port番号
        """
        self._ser = myserial.Serial(com, 115200, timeout=1)

    def led(self):
        u"""
        LEDを点灯させる
        """
        self._ser.write(self._LED)
        self._ser.read()    # 0x4f

    def receive(self):
        u"""
        赤外線を受信する
        :rtype:  str
        :return: 受信したデータ
        """
        self._ser.write(self._RECEIVE)
        self._ser.read(1)                # 0x59
        print(u"受信開始")
        self._ser.read(1)                # 0x53

        data = hexlify(self._ser.read(240))
        self._ser.read(1)                # 0x45
        print(u"受信データ:", data)
        return data

    def transmit(self, hex_data, channel):
        u"""
        赤外線を送信する
        :param str hex_data: 送信する16進数データ
        :param str channel:  送信部
        """
        binData = a2b_hex(hex_data)
        self._ser.write(self._TRANSMIT)
        self._ser.read(1)               # 0x59
        self._ser.write(channel)        # チャンネルの指定
        self._ser.read(1)               # 0x59
        self._ser.write(binData)        # データの送信
        self._ser.read(1)               # 0x45

    def close(self):
        u"""
        接続を閉じる
        """
        self._ser.close()


if __name__ == '__main__':
    por = PC_OP_RS1()

    try:
        # 受信したデータをそのまま送信する
        por.connect(2)
        por.led()                   # LEDの点灯
        data = por.receive()        # 赤外線の受信
        por.transmit(data, por.ch1) # 赤外線の送信

    except:
        ex, ms, tb = sys.exc_info()
        print("\nex -> \t", type(ex))
        print(ex)
        print("\nms -> \t", type(ms))
        print(ms)
        print("\ntb -> \t", type(tb))
        print(tb)

        print("\n=== and print_tb ===")
        traceback.print_tb(tb)

    finally:
        por.close()