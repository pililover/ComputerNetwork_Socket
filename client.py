import socket
import json
from PIL import Image, ImageTk
from PyQt6.QtCore import Qt, QBuffer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QtWidgets
import io
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pynput.keyboard
import Account
import gui

HOST = "127.0.1.1"
PORT = 64444
img_bytes = b'\x00\x01\x02...'
# Replace with actual binary image data

class Start(tk.Tk):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.title("Start")

        self.protocol("WM_DELETE_WINDOW", self.start_closing)

        self.label = tk.Label(self, text="Enter ID:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.txtID = tk.Entry(self, width=20)
        self.txtID.grid(row=0, column=1, padx=10, pady=10)

        self.butStart = tk.Button(self, text="Start", width=10, command=self.butStart_click)
        self.butStart.grid(row=0, column=2, padx=10, pady=10)

    def start_closing(self):
        try:
            self.client.send_command("QUIT")
        except Exception as ex:
            pass
        self.destroy()

    def butStart_click(self):
        try:
            self.client.send_command("STARTID")
            self.client.send_data(self.txtID.get())
            response = self.client.receive_data()
            messagebox.showinfo("Start Result", response)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

class Kill(tk.Tk):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.title("Kill")

        self.protocol("WM_DELETE_WINDOW", self.kill_closing)

        self.label = tk.Label(self, text="Enter ID:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.txtID = tk.Entry(self, width=20)
        self.txtID.grid(row=0, column=1, padx=10, pady=10)

        self.butNhap = tk.Button(self, text="Kill", width=10, command=self.butNhap_click)
        self.butNhap.grid(row=0, column=2, padx=10, pady=10)

    def butNhap_click(self):
        try:
            self.client.send_command("KILLID")
            self.client.send_data(self.txtID.get())
            response = self.client.receive_data()
            messagebox.showinfo("Kill Result", response)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def kill_closing(self):
        try:
            self.client.send_command("QUIT")
        except Exception as ex:
            pass
        self.destroy()

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.Cli_Sock = None
        self.network_file = None
        self.root = None  # Store the main Tkinter window reference here

        self.connect(self.host)  # Automatically connect on initialization

    def connect(self, ip):
        """Connect to the server."""
        try:
            self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        # handle_response("PROCESS"

    def register(Cli_Sock, Cli_Addr):
        user = Cli_Sock.recv(1024).decode("utf8")
        print("Client register: " + Cli_Sock)
        print("Username: ", user)
        Cli_Sock.sendall(user.encode('utf8'))

        password = Cli_Sock.recv(1024).decode("utf8")
        print("Password: ", password)
        Cli_Sock.sendall(password.encode('utf8'))

        acc = Account(user, password)
        valid_acc = acc.checkAvailable()

        if valid_acc == True:
            Cli_Sock.sendall(bytes("Account is available", "utf8"))
        else:
            Cli_Sock.sendall(bytes("Account is not available", "utf8"))
            acc.createAccount()

        print("Register process is done")

    def login(Cli_Sock, Cli_Addr):
        user = Cli_Sock.recv(1024).decode("utf8")
        print("Client login: " + Cli_Sock)
        print("Username: ", user)
        Cli_Sock.sendall(user.encode('utf8'))

        password = Cli_Sock.recv(1024).decode("utf8")
        print("Password: ", password)
        Cli_Sock.sendall(password.encode('utf8'))

        acc = Account(user, password)
        valid_acc = acc.checkAvailable()

        if valid_acc == True:
            Cli_Sock.sendall(bytes("Login success", "utf8"))
        else:
            Cli_Sock.sendall(bytes("Login fail", "utf8"))

        print("Login process is done")

    def deleteOnlineAccount(user, password, addr):
        try:
            with open('AccountLive.json', 'r') as file:
                file_data = json.load(file)

            if Account(user, password).isOnlineAccountStored(file_data, user, password, addr):
                remaining_accounts = []
                for stored_user, stored_password, stored_addr in zip(file_data["Account"], file_data["Password"], file_data["Address"]):
                    if stored_user == user and stored_password == password and stored_addr == addr:
                        continue
                    remaining_accounts.append(
                        {"Account": stored_user, "Password": stored_password, "Address": stored_addr})

                with open('AccountLive.json', 'w') as data_file:
                    json.dump(remaining_accounts, data_file, indent=4)
                print("Deleting success!")
                return True
            else:
                print("No account found!")
                return False
        except Exception as e:
            print("Error: ", str(e))
            return False

    # json file structure
    # {
    #   "Account": ["user1", "user2", ...],
    #   "Password": ["pass1", "pass2", ...],
    #   "Address": ["addr1", "addr2", ...]
    # }

    def logout(Cli_Sock, Cli_Addr, user, password):
        if Account.deleteOnlineAccount(user, password, Cli_Addr):
            try:
                Cli_Sock.sendall(bytes("Logout success", "utf8"))
            except:
                pass
        print("Logout process is done")

    def exit(Cli_Sock, Cli_Addr, user, password):
        Account.deleteOnlineAccount(user, password, Cli_Addr)
        try:
            Cli_Sock.sendall(bytes("Exit success", "utf8"))
        except:
            pass
        Cli_Sock.close()
        print("Exit process is done")

    def mainloop(self):
        if self.root:
            self.root.mainloop()


def blank():
    root = tk.Tk()
    text = tk.Label(root, text="This is a blanked scene!")
    text.pack(padx=20, pady=20)

    root.mainloop()


# Create a Client instance
client = Client(HOST, PORT)

# Create a GUI instance and pass in the client
gui = GUI(client)

# Run the GUI
gui.run()
