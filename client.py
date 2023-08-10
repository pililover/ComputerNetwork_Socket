import socket
import json
from PIL import Image, ImageTk
from PyQt6.QtCore import Qt, QBuffer
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, \
    QMessageBox, QFileDialog, QtWidgets
import io
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pynput.keyboard
from io import StringIO

HOST = "127.0.1.1"
PORT = 64444
img_bytes = b'\x00\x01\x02...'
# Replace with actual binary image data


class Account:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def checkAvailable(self):
        with open("account.csv", "r") as fin:
            for line in fin:
                user, password = line.strip().split(',')
                if user == self.user and password == self.password:
                    return True
        return False

    def addNewAcc2File(self):
        with open("account.csv", "a") as fin:
            fin.write(self.user + "," + self.password + "\n")

    def createAccount(self):
        if not self.checkAvailable():
            self.addNewAcc2File()
            print("Create account success")
            return True
        else:
            print("Create account fail")
            return False

    def isOnlineAccountStored(self, user, password, Cli_Addr):
        with open("AccountLive.json", "r") as file:
            file_data = json.load(file)
        for stored_user, stored_password, stored_Cli_Addr in zip(file_data["Account"], file_data["Password"], file_data["Address"]):
            if stored_user == user and stored_password == password and stored_Cli_Addr == Cli_Addr:
                return True
        return False

    def storeOnlineAccount(self, Cli_Addr):
        account_info = {"Account": self.user,
                        "Password": self.password, "Address": Cli_Addr}

        # Load the existing JSON data
        try:
            with open("AccountLive.json", "r") as file:
                file_data = json.load(file)
        except FileNotFoundError:
            file_data = {"Account": [], "Password": [], "Address": []}

        # Check for duplicates before appending to the list
        if not self.isOnlineAccountStored(self.user, self.password, Cli_Addr):
            file_data["Account"].append(account_info["Account"])
            file_data["Password"].append(account_info["Password"])
            file_data["Address"].append(account_info["Address"])

            with open("AccountLive.json", "w") as file:
                json.dump(file_data, file, indent=4)

            return True
        else:
            return False


class Keylog(QtWidgets.QWidget):
    def __init__(self, client):
        self.client = client
        self.init_ui()

    def init_ui(self):
        # ... (your existing init_ui function)
        self.button1 = QtWidgets.QPushButton('HOOK', self)
        self.button1.clicked.connect(self.hook_button_clicked)

        self.button2 = QtWidgets.QPushButton('UNHOOK', self)
        self.button2.clicked.connect(self.unhook_button_clicked)

        self.button3 = QtWidgets.QPushButton('PRINT', self)
        self.button3.clicked.connect(self.print_button_clicked)

        self.txtKQ = QtWidgets.QTextEdit(self)

        self.butXoa = QtWidgets.QPushButton('Clear', self)
        self.butXoa.clicked.connect(self.clear_button_clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.txtKQ)
        layout.addWidget(self.butXoa)

        self.setLayout(layout)
        self.setWindowTitle('Keylog')

    def hook_button_clicked(self):
        command = "HOOK\n"
        # You need to send this data to the server here
        self.client.send_command(command)
        pass

    def unhook_button_clicked(self):
        command = "UNHOOK\n"
        # You need to send this data to the server here
        self.client.send_command(command)
        pass

    def print_button_clicked(self):
        command = "PRINT\n"
        self.client.send_command(command)
        data = self.client.receive_data()  # Replace with actual receive logic
        text = ''.join(data)
        self.txtKQ.insert(tk.END, text)

    def clear_button_clicked(self):
        self.txtKQ.delete('1.0', tk.END)

    def run(self):
        self.root.mainloop()


class Process:
    def __init__(self, client):
        self.client = client

        def kill_click():
            try:
                self.client.send_data("KILL")
                view_kill = Kill(self.client)
                view_kill.run()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def view_click():
            try:
                self.client.send_data("XEM")
                soprocess = int(self.client.receive_data())
                for _ in range(soprocess):
                    s1 = self.client.receive_data()
                    s2 = self.client.receive_data()
                    s3 = self.client.receive_data()
                    one = (s1, s2, s3)
                    self.process_list.insert("", "end", values=one)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def start_click():
            try:
                self.client.send_data("START")
                view_start = Start(self.client)
                view_start.run()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def delete_click():
            if self.process_list.selection():
                selected_item = self.process_list.selection()[0]
                self.process_list.delete(selected_item)

        # Buttons
        kill_button = tk.Button(
            self, text="Kill", width=10, command=kill_click)
        kill_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(self, text="Xem", width=10, command=view_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        start_button = tk.Button(
            self, text="Start", width=10, command=start_click)
        start_button.grid(row=0, column=2, padx=10, pady=10)

        delete_button = tk.Button(
            self, text="Xóa", width=10, command=delete_click)
        delete_button.grid(row=0, column=3, padx=10, pady=10)

        # TreeView for Process List
        self.process_list = ttk.Treeview(self, columns=(
            "Name Process", "ID Process", "Count Thread"), show="headings")
        self.process_list.heading("#1", text="Name Process")
        self.process_list.heading("#2", text="ID Process")
        self.process_list.heading("#3", text="Count Thread")
        self.process_list.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        # ... (other widgets and settings)

        self.protocol("WM_DELETE_WINDOW", self.process_closing)

    def process_closing(self):
        self.client.send_data("QUIT")
        self.client.close()
        self.destroy()

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

class Kill(tk.Toplevel):
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


# Create the main GUI window


class GUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()  # Create the main GUI window
        self.root.title("Client")  # Set the title of the window

    def clientScene(self):
        root = tk.Tk()
        root.title("Client")
        # Input Box
        text = tk.Label(self.root, text="Enter IP:")
        text.grid(row=0, column=0, pady=10)

        self.inputBox = tk.Entry(self.root, width=50)
        self.inputBox.grid(row=0, column=1, columnspan=3, pady=10)

        # Connect Button
        connectButt = tk.Button(self.root, text="Connect",
                                width=10, command=self.client.connect)
        connectButt.grid(row=0, column=6, padx=10, pady=10)

        # Process Running
        processButt = tk.Button(root, text="Process Running",
                                padx=20, pady=20, command=self.client.process_click)
        processButt.grid(row=1, column=0, padx=40, pady=10, columnspan=2)

        # Application Running
        appButt = tk.Button(root, text="App Running", padx=30,
                            pady=20, command=self.client.app_click)
        appButt.grid(row=1, column=2, pady=10)

        # Shut Down
        shutDownButt = tk.Button(
            root, text="Shut Down", padx=35, pady=20, command=self.client.shutdown_click)
        shutDownButt.grid(row=2, column=0, padx=40, pady=10, columnspan=2)

        # Screenshot
        screenShotButt = tk.Button(
            root, text="Screenshot", padx=34, pady=20, command=self.client.pic_click)
        screenShotButt.grid(row=2, column=2, pady=10)

        # Keystroke
        keyStrokeButt = tk.Button(
            root, text="Keystroke", padx=39, pady=20, command=self.client.key_lock_click)
        keyStrokeButt.grid(row=3, column=0, padx=40, pady=10, columnspan=2)

        # Registry
        registryButt = tk.Button(
            root, text="Edit Registry", padx=33, pady=20, command=self.client.registry_click)
        registryButt.grid(row=3, column=2, pady=10)

        # Exit
        exit = tk.Button(root, text="Quit", bg="red", padx=30,
                         pady=10, command=self.client.exit_click)
        exit.grid(row=2, column=6, padx=10, pady=20)

        root.mainloop()

    def processScene(self):
        process_window = Process(self.client)
        process_window.mainloop()

    def appScene(self):

        app_window = tk.Tk()
        app_window.title("App")

        def kill_click():
            try:
                self.client.send_data("KILL")
                view_kill = Kill(self.client)
                view_kill.run()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def view_click():
            try:
                self.client.send_data("XEM")
                soprocess = int(self.client.receive_data())
                for _ in range(soprocess):
                    s1 = self.client.receive_data()
                    if s1 == "ok":
                        s1 = self.client.receive_data()
                        s2 = self.client.receive_data()
                        s3 = self.client.receive_data()
                        one = (s1, s2, s3)
                        self.app_list.insert("", "end", values=one)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def start_click():
            try:
                self.client.send_data("START")
                view_start = Start(self.client)
                view_start.run()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def delete_click():
            # Implement the delete action
            pass

        # TreeView for App List
        self.app_list = ttk.Treeview(app_window, columns=(
            "Name App", "ID App", "Count Thread"), show="headings")
        self.app_list.heading("#1", text="Name App")
        self.app_list.heading("#2", text="ID App")
        self.app_list.heading("#3", text="Count Thread")
        self.app_list.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        # Buttons
        kill_button = tk.Button(app_window, text="Kill",
                                width=10, command=kill_click)
        kill_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(app_window, text="Xem",
                                width=10, command=view_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        start_button = tk.Button(
            app_window, text="Start", width=10, command=start_click)
        start_button.grid(row=0, column=2, padx=10, pady=10)

        app_window.mainloop()

    def keystrokeScene(self):

        key_window = tk.Tk()
        key_window.title("Keystroke Log")

        def hook_click():
            self.key_listener = pynput.keyboard.Listener(
                on_press=self.on_key_press)
            self.key_listener.start()

        def unhook_click():
            if hasattr(self, 'key_listener'):
                self.key_listener.stop()

        def print_click():
            try:
                with open("keylog.txt", "r") as f:
                    keystrokes = f.read()
                    self.txtKQ.delete(1.0, tk.END)  # Clear existing text
                    self.txtKQ.insert(tk.END, keystrokes)
            except Exception as e:
                print(str(e))

        def delete_click():
            try:
                with open("keylog.txt", "w") as f:
                    f.truncate(0)  # Clear the file content
                self.txtKQ.delete(1.0, tk.END)  # Clear the Text widget
            except Exception as e:
                print(str(e))

        # Buttons
        hook_button = tk.Button(
            key_window, text="Hook", width=10, command=hook_click)
        hook_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(
            key_window, text="Unhook", width=10, command=unhook_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        delete_button = tk.Button(
            key_window, text="Xóa", width=10, command=delete_click)
        delete_button.grid(row=0, column=2, padx=10, pady=10)

        start_button = tk.Button(
            key_window, text="In", width=10, command=print_click)
        start_button.grid(row=0, column=3, padx=10, pady=10)

        # KeyLog text box
        self.txtKQ = tk.Text(key_window, width=50, height=20)
        self.txtKQ.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        key_window.mainloop()

    def registryScene(self):

        self.root = tk.Tk()
        self.root.title("Registry")

        def butSend_click():
            operation = self.opApp.get()
            link = self.txtLink.get()
            name_value = self.txtNameValue.get()
            value = self.txtValue.get()
            type_value = self.opTypeValue.get()

            # Send data to the server and receive response
            self.client.send_command("SEND")
            self.client.send_data(operation)
            self.client.send_data(link)
            self.client.send_data(name_value)
            self.client.send_data(value)
            self.client.send_data(type_value)
            response = self.client.receive_data()

            # Update the result textbox
            self.txtKQ.insert(tk.END, response + "\n")            

        def butBro_click():
            try:
                # Open the file dialog to choose a .reg file
                file_path = filedialog.askopenfilename(filetypes=[("Registry Files", "*.reg")])

                if file_path:
                    # Update the file path in the entry widget
                    self.txtBro.delete(0, tk.END)  # Clear existing content
                    self.txtBro.insert(0, file_path)

                    # Read the content of the selected file and populate the text box
                    with open(file_path, "r") as file:
                        reg_content = file.read()
                        self.txtReg.delete(1.0, tk.END)  # Clear existing content
                        self.txtReg.insert(tk.END, reg_content)
            except Exception as e:
                messagebox.showerror("Error", str(e))


        def button1_click():
            pass


        def butXoa_click():
            self.txtKQ.delete(1.0, tk.END)
            pass

        self.butBro = tk.Button(
            self.root, text="Browser...", command=butBro_click, width=15)
        self.butBro.grid(row=0, column=3, padx=10, pady=10)

        self.butSend = tk.Button(
            self.root, text="Gửi nội dung", pady=33, command=butSend_click, width=15)
        self.butSend.grid(row=1, column=3, padx=10,  pady=10)

        self.txtBro = tk.Entry(self.root, width=67)
        self.txtBro.grid(row=0, column=0, padx=10, pady=10)

        self.txtReg = tk.Text(self.root, height=5, width=50)
        self.txtReg.grid(row=1, column=0, padx=10, pady=10)

        self.groupBox1 = ttk.LabelFrame(
            self.root, text="  Sửa giá trị trực tiếp  ")
        self.groupBox1.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        self.opApp = ttk.Combobox(self.groupBox1, values=[
                                  "Get value", "Set value", "Delete value", "Create key", "Delete key"])
        self.opApp.set("Chọn chức năng")
        self.opApp.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.txtLink = tk.Entry(self.groupBox1, width=50)
        self.txtLink.insert(0, "Đường dẫn")
        self.txtLink.grid(row=1, column=0, columnspan=2,
                          padx=10, pady=10, sticky=tk.W)

        self.txtValue = tk.Entry(self.groupBox1, width=20)
        self.txtValue.insert(0, "Name value")
        self.txtValue.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.txtNameValue = tk.Entry(self.groupBox1, width=20)
        self.txtNameValue.insert(0, "Value")
        self.txtNameValue.grid(row=2, column=1, padx=10, pady=10)

        self.opTypeValue = ttk.Combobox(self.groupBox1, values=[
                                        "String", "Binary", "DWORD", "QWORD", "Multi-String", "Expandable String"])
        self.opTypeValue.set("Kiểu dữ liệu")
        self.opTypeValue.grid(row=2, column=2, padx=10, pady=10)

        self.txtKQ = tk.Text(self.groupBox1, height=5, width=60)
        self.txtKQ.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.button1 = tk.Button(
            self.groupBox1, text="Gởi", command=button1_click, width=15)
        self.button1.grid(row=4, column=0, padx=10, pady=10, sticky=tk.E)

        self.butXoa = tk.Button(
            self.groupBox1, text="Xóa", command=butXoa_click, width=15)
        self.butXoa.grid(row=4, column=2, padx=10, pady=10, sticky=tk.W)

        self.root.mainloop()

    def ScreenshotScene(self):
        self.root = tk.Tk()
        self.root.title("Pic")

        # Create the picture label
        self.picture = tk.Label(self.root)
        self.picture.pack(side=tk.LEFT)

        # Create the Take button
        self.butTake = tk.Button(
            self.root, text="Screenshot", command=self.butTake_click)
        self.butTake.pack(side=tk.TOP)

        # Create the Save button
        self.button1 = tk.Button(
            self.root, text="SAVE", command=self.buttonSAVE_click)
        self.button1.pack(side=tk.TOP)

    def butTake_click(self):
        try:
            self.Cli_Sock.sendall(b"TAKEPIC")
            img_bytes = self.Cli_Sock.recv(4096)

            # Display screenshot in a new tab
            new_tab = ttk.Frame(self.tabs)
            tab_label = tk.Label(new_tab)
            tab_pil_img = Image.open(io.BytesIO(img_bytes))
            tab_img = ImageTk.PhotoImage(tab_pil_img)
            tab_label.config(image=tab_img)
            tab_label.image = tab_img
            tab_label.pack()

            save_btn = ttk.Button(
                new_tab, text="Save", command=lambda: self.buttonSAVE_click(img_bytes))
            save_btn.pack()

            self.tabs.add(new_tab, text="Screenshot")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def buttonSAVE_click(self):
        # Show the save file dialog
        filename = filedialog.asksaveasfilename(
            title="Save Screenshot",
            filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")),
            defaultextension=".png"
        )
        if filename:
            with open(filename, 'wb') as f:
                f.write(img_bytes)

    def pic_closing(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.Cli_Sock.sendall(b"EXIT")
            self.Cli_Sock.close()

    def run(self):
        self.root.mainloop()  # Start the main event loop


# Create a Client instance
client = Client(HOST, PORT)

# Create a GUI instance and pass in the client
gui = GUI(client)

# Run the GUI
gui.run()
