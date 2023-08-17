import socket
import json
import sys
from PIL import Image, ImageTk
import io
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pynput.keyboard
import gui
import os

HOST = '0.0.0.0'
PORT = 4444
img_bytes = b'\x00\x01\x02...'
# Replace with actual binary image data


class Client:
    def __init__(self, port):
        self.port = port
        self.Cli_Sock = None
        self.network_file = None
        self.gui = gui.GUI(self)
        self.root = self.gui.root  # Store the main Tkinter window reference here
        self.ip = self.gui.ip    
        #print(self.ip)
        # self.connect(self.host)  # Automatically connect on initialization
    def connect(self,ip):
        """Connect to the server."""
        try:
            self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(ip)
            self.Cli_Sock.connect((ip, self.port))
            self.ns = self.Cli_Sock.makefile('rwb')
            self.nr = self.ns.makefile('r')
            self.nw = self.ns.makefile('w')
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
            self.nw.write((command + "\n").encode())
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
            self.nw.write((data + "\n").encode())
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
            return self.nr.readline().decode().strip()
        except socket.timeout as ex:
            messagebox.showerror("Error", f"Timeout: {ex}")
            return ""
        except socket.error as ex:
            messagebox.showerror("Error", f"Error receiving data: {ex}")
            return ""

    def handle_response(self, res):
        """Handle the response from the server based on the response type."""
        if res == "APPLICATION":
            data = self.receive_data()
            # Display data in a tkinter widget
            tk.Label(self.root, text=data).pack()
        elif res == "SHUTDOWN":
            data = self.receive_data()
            # Display data in a tkinter widget
            tk.Label(self.root, text=data).pack()
        elif res == "REGISTRY":
            data = self.receive_data()
            # Display data in a tkinter widget
            tk.Label(self.root, text=data).pack()

    def app_click(self):
        """Send the APPLICATION command to the server and handle the response."""
        self.send_command("APPLICATION")
        self.handle_response("APPLICATION")

    def shutdown_click(self):
        """Send the SHUTDOWN command to the server and handle the response."""
        self.send_command("SHUTDOWN")
        self.handle_response("SHUTDOWN")

    def registry_click(self):
        """Send the REGISTRY command to the server and handle the response."""
        self.send_command("REGISTRY")
        self.handle_response("REGISTRY")

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
                    # Close main Tkinter window
                    #if (self.root is not None): 
                except Exception as ex:
                    messagebox.showerror("Error", f"Error quitting: {ex}")
            
            #self.destroy()
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


def blank():
    root = tk.Tk()
    text = tk.Label(root, text="This is a blanked scene!")
    text.pack(padx=20, pady=20)

    root.mainloop()


# Create a Client instance
client = Client(PORT)

# Create a GUI instance and pass in the client
gui = gui.GUI(client)
# client.root = gui.root

# Run the GUI
gui.run()