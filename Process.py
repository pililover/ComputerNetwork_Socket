from PIL import Image, ImageTk
from PyQt6.QtCore import Qt, QBuffer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QtWidgets
import io
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


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

        self.butStart = tk.Button(
            self, text="Start", width=10, command=self.butStart_click)
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

        self.butNhap = tk.Button(
            self, text="Kill", width=10, command=self.butNhap_click)
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


class Process(tk.Tk):
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
