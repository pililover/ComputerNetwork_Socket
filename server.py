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

HOST = "127.0.1.1"
PORT = 66789

FONT = ("Arial", 20, "bold")
LOGIN = "login"
REGISTER = "register"
LOGOUT = "logout"
EXIT = "exit"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
    s.listen(1)
    print("Waiting for Client")
    conn, addr = s.accept()
    print("Connected by ", addr)
except s.timeout as timeout:
    print("Timeout to server: ", addr)
    conn.close()
except s.error as error:
    print("Disconnected to server: ", addr)
    conn.close()


def doServer(Cli_Sock, Cli_Addr):
    try:
        while True:
            print("Server is running... Wait a second")
            Cli_Sock, Cli_Addr = s.accept()
            threading.Thread(target=doClient, args=(
                Cli_Sock, Cli_Addr)).start()
    except s.timeout as timeout:
        print("Timeout to server: ", Cli_Addr)
        s.close()
    finally:
        s.close()


def doClient(Cli_Sock, Cli_Addr):
    try:
        while True:
            option = Cli_Sock.recv(1024).decode("utf8")
            print("Client option: " + option)
            if option == LOGIN:
                Cli_Sock.sendall(bytes("Login success", "utf8"))

            elif option == REGISTER:
                Cli_Sock.sendall(bytes("Register success", "utf8"))

            elif option == LOGOUT:
                Cli_Sock.sendall(bytes("Logout success", "utf8"))

            elif option == EXIT:
                Cli_Sock.sendall(bytes("Exit success", "utf8"))
                break
            elif option == "TAKEPIC":
                Screenshot(Cli_Sock)
            elif option == "SHUTDOWN":
                ShutDown()
            elif option == "REGISTRY":
                PCRegistry(Cli_Sock)
            else:
                Cli_Sock.sendall(bytes("Option not found", "utf8"))
                break
        Cli_Sock.close()
        print("Client close: ", Cli_Addr)
    except s.timeout as timeout:
        print("Timeout to server: ", Cli_Addr)
        Cli_Sock.close()
    except s.error as error:
        print("Disconnected to server: ", Cli_Addr)
        Cli_Sock.close()
    finally:
        Cli_Sock.close()


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


def register(Cli_Sock, Cli_Addr):
    user = Cli_Sock.recv(1024).decode("utf8")
    print("Client register: " + s)
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
    print("Client login: " + s)
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
    if deleteOnlineAccount(user, password, Cli_Addr):
        try:
            Cli_Sock.sendall(bytes("Logout success", "utf8"))
        except:
            pass
    print("Logout process is done")


def exit(Cli_Sock, Cli_Addr, user, password):
    deleteOnlineAccount(user, password, Cli_Addr)
    try:
        Cli_Sock.sendall(bytes("Exit success", "utf8"))
    except:
        pass
    Cli_Sock.close()
    print("Exit process is done")


def sendResponse(Client_Socket, res):
    Client_Socket.sendall(bytes(res, "utf8"))


def PCRegistryKey(link):
    base_key = None
    if "\\" in link:
        base_link = link[:link.index("\\")].upper()
        if base_link == "HKEY_CLASSES_ROOT":
            base_key = "HKEY_CLASSES_ROOT"
        elif base_link == "HKEY_CURRENT_USER":
            base_key = "HKEY_CURRENT_USER"
        elif base_link == "HKEY_LOCAL_MACHINE":
            base_key = "HKEY_LOCAL_MACHINE"
        elif base_link == "HKEY_USERS":
            base_key = "HKEY_USERS"
        elif base_link == "HKEY_CURRENT_CONFIG":
            base_key = "HKEY_CURRENT_CONFIG"
    return base_key


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
                    value_bytes = bytes(int(byte) for byte in value.split())
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


def PCRegistry(Cli_Sock):
    s = Cli_Sock.recv(4092).decode("utf8")

    # Parse the received data to get base_key, link, value_name, value, and value_type
    # Format of data: "<base_key>;<link>;<value_name>;<value>;<value_type>"
    base_key, link, value_name, value, value_type = s.split(";")

    if value_type == "DELETE_VALUE":
        res = PCRemoveValue(base_key, link, value_name)
    elif value_type == "DELETE_KEY":
        res = PCRemoveKey(base_key, link)
    else:
        res = PCSetValue(base_key, link, value_name, value, value_type)

    sendResponse(Cli_Sock, res)


def Screenshot(Cli_Sock):
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
        Cli_Sock.sendall(img_bytes)
    except Exception as ex:
        Cli_Sock.sendall(bytes("Error: " + str(ex), "utf8"))


def ShutDown():
    # Thuong thi os.name cua Linux hoac Mac la "posix"
    system_name = platform.system()
    if system_name == "Windows":
        subprocess.run(["shutdown", "-s"])
    elif system_name == "Darwin" or system_name == "Linux":
        os.system("sudo shutdown -h now")
    else:
        print("Shutdown command not supported on this platform.")
