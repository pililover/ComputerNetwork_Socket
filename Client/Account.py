# Account.py
import json


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
