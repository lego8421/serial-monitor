import sys
import time
import argparse
import threading

import serial
import serial.tools.list_ports as stl


def list_serialports():
    info_list = []

    def __is_port(port):
        return (port.vid == 0x10C4 and port.pid == 0xEA60)

    ports = [port for port in stl.comports() if __is_port(port)]
    for port in ports:
        info_list.append(port.device)

    return info_list

class SerialMonitor:
    def __init__(self, port, baud=921600):
        self.port = port
        self.serial_port = None
        self.baudrate = baud
        self.is_uploading = False
        self.connected_modules = {}
        self.module_state = {}
        self.module_disconnect_timeout = 3
        self.current_interpreter_index = -1
        self.current_interpreter_state = 0

        if self.port is None:
            print("Not found serial ports")
            return

        self.serial_port = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0.1, write_timeout=0)
        self.stop_signal = False

        self.show_serial = False

    def run(self):
        if self.serial_port is None:
            return

        self.stop_signal = False
        threading.Thread(target=self.handle_received, daemon=True).start()
        while not self.stop_signal:
            input_data = input()

            if input_data == "exit":
                self.stop_signal = True

            time.sleep(0.5)

    def handle_received(self):
        while not self.stop_signal:
            if not self.serial_port.is_open:
                self.stop_signal = True
                break

            recved = self.serial_port.read()
            if recved != b"":
                sys.stdout.buffer.write(recved)
                sys.stdout.buffer.flush()

def main(port, baud):
    if port is None:
        port_list = list_serialports()

        if len(port_list) == 0:
            print("Not found")
            return
        elif len(port_list) == 1:
            port = port_list[0]
        else:
            print("scan.....")
            for index, name in enumerate(port_list):
                print(index, name)
            print("select: ", end="")

            input_data = input()
            index = int(input_data)

            port = port_list[index]

    uploader = SerialMonitor(port, baud)
    uploader.run()

if __name__ == '__main__':
    try:
        cmd_parser = argparse.ArgumentParser(description='Display serialport monitor')
        cmd_parser.add_argument('-p', '--port', default='None', help='the serialport device')
        cmd_parser.add_argument('-b', '--baud', default='921600', help='the serialport baudrate')

        args = cmd_parser.parse_args()

        if args.port == "None":
            port = None
        else:
            port = args.port

        baud = int(args.baud)

        main(port, baud)
    except Exception as e:
        print('\na fatal error occurred: %s' % e)
