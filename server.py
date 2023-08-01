import socket
import threading

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
            Client_Socket, Client_Address = s.accept()
            threading.Thread(target=doClient, args=(Client_Socket, Client_Address)).start()
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
    
    print ("Register process is done")
    
def login(Cli_Sock, Cli_Addr):
    
    
