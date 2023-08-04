import tkinter as tk
from tkinter import messagebox
import socket
import subprocess

HOST = "127.0.1.1"
PORT = 64444


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.Cli_Sock = None
        self.network_file = None

    def connect(self, ip):
        """Connect to the server."""
        try:
            self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Cli_Sock.connect((ip, self.port))
            self.network_file = self.Cli_Sock.makefile('rw')
            messagebox.showinfo(
                "Connected", "Connected to the server successfully")
        except socket.error as ex:
            messagebox.showerror(
                "Error", f"Failed to connect to the server: {ex}")
            self.Cli_Sock = None
            self.network_file = None

    def send_command(self, command):
        """Send a command to the server."""
        if self.Cli_Sock is None:
            messagebox.showerror("Error", "Not connected to the server")
            return
        try:
            self.network_file.write(command + "\n")
            self.network_file.flush()
        except socket.timeout as ex:
            messagebox.showerror(
                "Error", f"Timeout while sending command to the server: {ex}")
        except socket.error as ex:
            messagebox.showerror(
                "Error", f"Failed to send command to the server: {ex}")

    def handle_response(self, res):
        """Handle the response from the server based on the response type."""
        # Add code to handle different types of responses from the server
        pass

    def app_click(self):
        """Send the APPLICATION command to the server and handle the response."""
        self.send_command("APPLICATION")
        # handle_response("APPLICATION")

    def shutdown_click(self):
        """Send the SHUTDOWN command to the server and handle the response."""
        self.send_command("SHUTDOWN")
        # handle_response("SHUTDOWN")

    def registry_click(self):
        """Send the REGISTRY command to the server and handle the response."""
        self.send_command("REGISTRY")
        # handle_response("REGISTRY")

    def exit_click(self):
        """Send the QUIT command to the server, close the connection, and exit the application."""
        if not messagebox.askokcancel("Quit", "Do you want to quit?"):
            return

        if (self.Cli_Sock is not None):
            try:
                # Send QUIT command to server
                self.send_command("QUIT")
                # Close socket connection
                self.Cli_Sock.close()
            except:
                pass

    def pic_click(self):
        """Send the TAKEPIC command to the server and handle the response."""
        self.send_command("TAKEPIC")
        # handle_response("TAKEPIC")

    def key_lock_click(self):
        """Send the KEYLOG command to the server and handle the response."""
        self.send_command("KEYLOG")
        # handle_response("KEYLOG")

    def process_click(self):
        """Send the PROCESS command to the server and handle the response."""
        self.send_command("PROCESS")
        # handle_response("PROCESS")

# Create the main GUI window


# Create a Client instance
client = Client(HOST, PORT)

# Create a GUI instance and pass in the client
# gui = GUI(client)

# Start the main event loop
#gui.root.mainloop()
