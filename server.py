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
        
