import socket
import sys
import tkinter as tk
from tkinter import messagebox
import gui
import logging

HOST = '127.0.0.1'
PORT = 4444
img_bytes = b'\x00\x01\x02...'
# Replace with actual binary image data


class Client:
    def __init__(self, port):
        self.port = port
        self.Cli_Sock = None
        self.network_file = None
    def connect(self,ip):
        """Connect to the server."""
        try:
            self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(ip)
            self.Cli_Sock.connect((ip, self.port))
            self.ns = self.Cli_Sock.makefile('rwb')
            self.nr = self.Cli_Sock.makefile('r')
            self.nw = self.Cli_Sock.makefile('w')
            messagebox.showinfo(
                "Connected", "Connected to the server successfully")
        except socket.error as ex:
            messagebox.showerror(
                "Error", f"Failed to connect to the server: {ex}")
            self.Cli_Sock = None
            self.ns = None
            self.nr = None
            self.nw = None

    def send_command(self, command):
        if self.Cli_Sock is None:
            messagebox.showerror("Error", "Not connected to the server")
            return
        try:
            self.nw.write(command)
            self.nw.flush()
        except socket.timeout as ex:
            messagebox.showerror("Error", f"Timeout: {ex}")
        except socket.error as ex:
            messagebox.showerror("Error", f"Error sending command: {ex}")

    def send_data(self, data):
        if self.Cli_Sock is None:
            messagebox.showerror("Error", "Not connected to the server")
            return
        try:
            self.nw.write(data)
            self.nw.flush()
        except socket.timeout as ex:
            messagebox.showerror("Error", f"Timeout: {ex}")
        except socket.error as ex:
            messagebox.showerror("Error", f"Error sending data: {ex}")

    def receive_data(self):
        if self.Cli_Sock is None:
            messagebox.showerror("Error", "Not connected to the server")
            return ""
        try:
            return self.nr.readline().strip()
        except socket.timeout as ex:
            messagebox.showerror("Error", f"Timeout: {ex}")
            return ""
        except socket.error as ex:
            messagebox.showerror("Error", f"Error receiving data: {ex}")
            return ""

    def handle_response(self, res):
        """Handle the response from the server based on the response type."""
        print(res)
        gui.GUI(self, res)
        if res == "APPLICATION":
            print(res)
        elif res == "SHUTDOWN":
            print("Shutting down")
            print(res)
        elif res == "REGISTRY":
            print(res)
        elif res == "TAKEPIC":
            print("Sending image")
            while True:
                filename = r"screenshot.png"
                with open(filename, 'wb') as fw:
                    while True:
                        print("Receiving data")
                        self.Cli_Sock.settimeout(20)  # Set a timeout of 20 seconds
                        data = self.Cli_Sock.recv(4096)
                        if not data:
                            break
                        fw.write(data)
                    fw.close()
                break 
            print("Done")
        elif res == "KEYLOG":
            print(res)
        elif res == "PROCESS":
            data = self.receive_data()
        elif res == "QUIT":
            data = self.receive_data()
        else:
            messagebox.showerror("Error", f"Unknown response: {res}")
            
    def app_click(self):
        """Send the APPLICATION command to the server and handle the response."""
        self.send_command("APPLICATION")
        self.handle_response("APPLICATION")

    def shutdown_click(self):
        """Send the SHUTDOWN command to the server and handle the response."""
        self.send_command("SHUTDOWN")
        self.handle_response("SHUTDOWN")

    def exit_click(self):
        """Send the QUIT command to the server, close the connection, and exit the application."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if (self.Cli_Sock is not None):
                try:
                    print("Quitting...")
                    # Send QUIT command to server
                    self.send_command("QUIT")
                    # Close socket connection
                    self.Cli_Sock.close()
                except Exception as ex:
                    messagebox.showerror("Error", f"Error quitting: {ex}")
            
            sys.exit(0)

    def pic_click(self):
        """Send the TAKEPIC command to the server and handle the response."""
        self.send_command("TAKEPIC")
        self.handle_response("TAKEPIC")

    def key_lock_click(self):
        """Send the KEYLOG command to the server and handle the response."""
        self.send_command("KEYLOG")
        self.handle_response("KEYLOG")

    def process_click(self):
        """Send the PROCESS command to the server and handle the response."""
        self.send_command("PROCESS")
        self.handle_response("PROCESS")

    # Create a Client instance

class clientScene:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()  # Create the main GUI window
        self.root.title("Client")  # Set the title of the window
        self.ip = None
        self.scene()
        self.root.mainloop()

    def scene(self):
        # Input Box
        text = tk.Label(self.root, text="Enter IP:")
        text.grid(row=0, column=0, pady=10)

        self.inputBox = tk.Entry(self.root, width=50)
        self.inputBox.grid(row=0, column=1, columnspan=3, pady=10)

        # Connect Button
        def connect_wrapper():
            logging.info("Connecting to the server...")
            ip = self.inputBox.get()
            self.client.connect(ip)
            self.ip = ip
            #print(self.inputBox.get())
            logging.info("Connected to the server")
        connectButt = tk.Button(self.root, text="Connect",
                                width=10, command=connect_wrapper)
        connectButt.grid(row=0, column=6, padx=10, pady=10)

        # Process Running
        processButt = tk.Button(self.root, text="Process Running",
                                padx=20, pady=20, command=self.client.process_click)
        processButt.grid(row=1, column=0, padx=40, pady=10, columnspan=2)

        # Application Running
        appButt = tk.Button(self.root, text="App Running", padx=30,
                            pady=20, command=self.client.app_click)
        appButt.grid(row=1, column=2, pady=10)

        # Shut Down
        shutDownButt = tk.Button(
            self.root, text="Shut Down", padx=35, pady=20, command=self.client.shutdown_click)
        shutDownButt.grid(row=2, column=0, padx=40, pady=10, columnspan=2)

        # Screenshot
        screenShotButt = tk.Button(
            self.root, text="Screenshot", padx=35, pady=20, command=self.client.pic_click)
        screenShotButt.grid(row=2, column=2, pady=10)

        # Keystroke
        keyStrokeButt = tk.Button(
            self.root, text="Keystroke", padx=39, pady=20, command=self.client.key_lock_click)
        keyStrokeButt.grid(row=3, column=0, padx=40, pady=10, columnspan=2)

        # Exit
        exit = tk.Button(self.root, text="Quit", bg="red", padx=53,
                         pady=20, command=self.client.exit_click)
        exit.grid(row=3, column=2, padx=10, pady=10)


clientScene(Client(PORT)) # Create a GUI instance and pass in the client