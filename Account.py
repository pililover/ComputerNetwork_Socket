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
