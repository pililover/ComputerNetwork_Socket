import socket
import sys
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import client

class Program:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns = None
    nr = None
    nw = None

    @staticmethod
    def main():
        root = Tk()
        app = client(master=root)
        app.mainloop()
        root.destroy()


if __name__ == "__main__":
    Program.main()
