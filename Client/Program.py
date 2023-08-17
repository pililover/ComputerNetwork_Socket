import sys
import socket
import threading
import time

from tkinter import Tk, Listbox, Button, END, SINGLE

class Program:
    client = None
    ns = None
    nr = None
    nw = None

    #def sendData(s):
    #    data = s.encode()
    #    Program.client.send(data)

    #def receiveData():
    #    data = Program.client.recv(1024)
    #    if not data:
    #        return None
    #    s = data.decode()
    #    return s
