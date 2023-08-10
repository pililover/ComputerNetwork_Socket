# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from PyQt6.QtCore import Qt, QBuffer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QtWidgets
import io
from io import BytesIO
import pynput.keyboard
import pynput.mouse
from Process import Start, Kill, Process
import Keylog
img_bytes = b'\x00\x01\x02...'

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
                file_path = filedialog.askopenfilename(
                    filetypes=[("Registry Files", "*.reg")])

                if file_path:
                    # Update the file path in the entry widget
                    self.txtBro.delete(0, tk.END)  # Clear existing content
                    self.txtBro.insert(0, file_path)

                    # Read the content of the selected file and populate the text box
                    with open(file_path, "r") as file:
                        reg_content = file.read()
                        # Clear existing content
                        self.txtReg.delete(1.0, tk.END)
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
