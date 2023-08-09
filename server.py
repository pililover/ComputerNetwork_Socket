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

HOST = "127.0.1.1"
PORT = 64444

FONT = ("Arial", 20, "bold")
LOGIN = "login"
REGISTER = "register"
LOGOUT = "logout"
EXIT = "exit"


class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

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
                if option == LOGIN:
                    conn.sendall(bytes("Login success", "utf8"))

                elif option == REGISTER:
                    conn.sendall(bytes("Register success", "utf8"))

                elif option == LOGOUT:
                    conn.sendall(bytes("Logout success", "utf8"))

                elif option == EXIT:
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

    def PCRegistryKey(self, conn):  # Renamed function
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

            conn.sendall(bytes(res, "utf8"))  # Directly send response
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
            self = conn.recv(4092).decode("utf8")

            # Parse the received data to get base_key, link, value_name, value, and value_type
            # Format of data: "<base_key>;<link>;<value_name>;<value>;<value_type>"
            base_key, link, value_name, value, value_type = self.split(";")

            if value_type == "DELETE_VALUE":
                res = Server.PCRemoveValue(base_key, link, value_name)
            elif value_type == "DELETE_KEY":
                res = Server.PCRemoveKey(base_key, link)
            else:
                res = Server.PCSetValue(
                    base_key, link, value_name, value, value_type)

            Server.send_response(conn, res)
        except Exception as ex:
            Server.send_response(conn, "Error: " + str(ex))

    def send_response(self, conn, response):
        conn.sendall(bytes(response, "utf8"))


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
