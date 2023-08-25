# gui.py
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import io
from io import BytesIO
import pynput.keyboard
import pynput.mouse
from Process import Start, Kill, Process
import Keylog
import whois
import Program
import subprocess
import os
import sys

img_bytes = b'\x00\x01\x02...'

# Create the main GUI window


class GUI:
    def __init__(self, client, data):
        self.client = client
        if data == "APPLICATION":
            self.appScene()
        # elif data == "TAKEPIC":
        #     self.ScreenshotScene()
        elif data == "REGISTRY":
            self.registryScene()
        elif data == "KEYLOG":
            self.keystrokeScene()
        elif data == "PROCESS":
            self.processScene()
            
    def startScene(self):
        start_scene = tk.Tk()
        start_scene.title("Start")
        text = tk.Label(start_scene, text="Enter Name:")
        text.grid(row=0, column=0, padx=10, pady=10)
        inputBox = tk.Entry(start_scene, width=30)
        inputBox.grid(row=0, column=1,pady=10)
        
        def clicked():
            self.start_app(inputBox.get())
        
        connectButt = tk.Button(start_scene, text="Start",
                                width=10, command=clicked)
        connectButt.grid(row=0, column=2, padx=10, pady=10)
        
        start_scene.mainloop()
    
    def start_app(self, app_name):
        try:
            self.client.Cli_Sock.send(f"run {app_name}".encode())
            response = self.client.Cli_Sock.recv(1024).decode()
            messagebox.showinfo("Response", response)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
        
    
    def processScene(self):
        process_window = Process(self.client)
        process_window.mainloop()

    def appScene(self):

        app_window = tk.Tk()
        app_window.title("App")

        # def get_running_apps(self):
        #     # Get the list of running applications on the server
        #     cmd = 'tasklist'
        #     proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        #     output = proc.communicate()[0].decode('utf-8')
        #     return output

        def kill_click():
            def submit():
                pid = entry.get()
                top.destroy()
                try:
                    self.client.Cli_Sock.send(f"kill {pid}".encode())
                    response = self.client.Cli_Sock.recv(1024).decode()
                    messagebox.showinfo("Response", response)
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            top = tk.Toplevel()
            top.title("Kill App")
            label = tk.Label(top, text="Enter the PID of the app to kill:")
            label.pack()
            entry = tk.Entry(top)
            entry.pack()
            submit_button = tk.Button(top, text="Submit", command=submit)
            submit_button.pack()
            #try:
                
            #     app_name = input("Enter the name of the app to kill: ")
            #     self.client.Cli_Sock.send(f"kill {app_name}".encode())
            #     response = self.client.recv(1024).decode()
            #     messagebox.showinfo("Response", response)
            # except Exception as ex:
            #     messagebox.showerror("Error", str(ex))

        def view_click():
            try:
                self.client.Cli_Sock.send("view".encode()) # Send the command to the server
                response = self.client.Cli_Sock.recv(4096).decode()  # Increased buffer size for more data
                print(response)
                for line in response.split("\n"):
                    columns = line.split("\t")
                    if len(columns) == 3:  # Expecting three columns: Image name, PID, Thread count
                        self.app_list.insert("", "end", values=columns)
                messagebox.showinfo("Response", response)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def start_click():
            #     self.client.send_data("START")
            #     view_start = Start(self.client)
            #     view_start.run()
                self.startScene()
                

        def delete_click():
            if self.app_list.selection():
                selected_item = self.app_list.selection()[0]
                app_name = self.app_list.item(selected_item)["values"][0]
                self.client.send(f"delete {app_name}".encode())
                response = self.client.recv(1024).decode()
                messagebox.showinfo("Response", response)
                self.app_list.delete(selected_item)

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

        view_button = tk.Button(app_window, text="View",
                                width=10, command=view_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        start_button = tk.Button(
            app_window, text="Start", width=10, command=start_click)
        start_button.grid(row=0, column=2, padx=10, pady=10)
        
        delete_button = tk.Button(
            app_window, text="Delete", width=10, command=delete_click) 
        delete_button.grid(row=0, column=3, padx=10, pady=10)

        app_window.mainloop()
        
    def keystrokeScene(self):

        key_window = tk.Tk()
        key_window.title("Keystroke Log")

        # Buttons
        hook_button = tk.Button(
            key_window, text="Hook", width=10, command=hook_click)
        hook_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(
            key_window, text="Unhook", width=10, command=unhook_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        delete_button = tk.Button(
            key_window, text="Clear", width=10, command=delete_click)
        delete_button.grid(row=0, column=2, padx=10, pady=10)

        start_button = tk.Button(
            key_window, text="Print", width=10, command=print_click)
        start_button.grid(row=0, column=3, padx=10, pady=10)

        # KeyLog text box
        self.txtKQ = tk.Text(key_window, width=50, height=20)
        self.txtKQ.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        def hook_click():
            self.client.Cli_Sock.send("HOOK".encode()) # Send the command to the server

        def unhook_click():
            self.client.Cli_Sock.send("UNHOOK".encode())

        def print_click():
            self.client.Cli_Sock.send("PRINT".encode())
            data = self.client.Cli_Sock.recv(5000).decode()
            self.textbox.insert(tk.END, data)

        def delete_click():
            self.textbox.delete("1.0", tk.END)

        key_window.mainloop()

    # def registryScene(self):

    #     self.root = tk.Tk()
    #     self.root.title("Registry")

    #     def butSend_click():
    #         operation = self.opApp.get()
    #         link = self.txtLink.get()
    #         name_value = self.txtNameValue.get()
    #         value = self.txtValue.get()
    #         type_value = self.opTypeValue.get()

    #         # Send data to the server and receive response
    #         self.client.send_command("SEND")
    #         self.client.send_data(operation)
    #         self.client.send_data(link)
    #         self.client.send_data(name_value)
    #         self.client.send_data(value)
    #         self.client.send_data(type_value)
    #         response = self.client.receive_data()

    #         # Update the result textbox
    #         self.txtKQ.insert(tk.END, response + "\n")

    #     def butBro_click():
    #         try:
    #             # Open the file dialog to choose a .reg file
    #             file_path = filedialog.askopenfilename(
    #                 filetypes=[("Registry Files", "*.reg")])

    #             if file_path:
    #                 # Update the file path in the entry widget
    #                 self.txtBro.delete(0, tk.END)  # Clear existing content
    #                 self.txtBro.insert(0, file_path)

    #                 # Read the content of the selected file and populate the text box
    #                 with open(file_path, "r") as file:
    #                     reg_content = file.read()
    #                     # Clear existing content
    #                     self.txtReg.delete(1.0, tk.END)
    #                     self.txtReg.insert(tk.END, reg_content)
    #         except Exception as e:
    #             messagebox.showerror("Error", str(e))

    #     def button1_click(self):
    #         s = "SEND"
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.opApp.get()
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.txtLink.get()
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.txtNameValue.get()
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.txtValue.get()
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.opTypeValue.get()
    #         self.nw.write(s + "\n")
    #         self.nw.flush()
    #         s = self.nr.readline().strip()
    #         self.txtKQ.insert(tk.END, s + "\n")

    #     def butXoa_click():
    #         self.txtKQ.delete(1.0, tk.END)

    #     self.butBro = tk.Button(
    #         self.root, text="Browser...", command=butBro_click, width=15)
    #     self.butBro.grid(row=0, column=3, padx=10, pady=10)

    #     self.butSend = tk.Button(
    #         self.root, text="Gửi nội dung", pady=33, command=butSend_click, width=15)
    #     self.butSend.grid(row=1, column=3, padx=10,  pady=10)

    #     self.txtBro = tk.Entry(self.root, width=67)
    #     self.txtBro.grid(row=0, column=0, padx=10, pady=10)

    #     self.txtReg = tk.Text(self.root, height=5, width=50)
    #     self.txtReg.grid(row=1, column=0, padx=10, pady=10)

    #     self.groupBox1 = ttk.LabelFrame(
    #         self.root, text="  Sửa giá trị trực tiếp  ")
    #     self.groupBox1.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

    #     self.opApp = ttk.Combobox(self.groupBox1, values=[
    #                               "Get value", "Set value", "Delete value", "Create key", "Delete key"])
    #     self.opApp.set("Chọn chức năng")
    #     self.opApp.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    #     self.txtLink = tk.Entry(self.groupBox1, width=50)
    #     self.txtLink.insert(0, "Đường dẫn")
    #     self.txtLink.grid(row=1, column=0, columnspan=2,
    #                       padx=10, pady=10, sticky=tk.W)

    #     self.txtValue = tk.Entry(self.groupBox1, width=20)
    #     self.txtValue.insert(0, "Name value")
    #     self.txtValue.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

    #     self.txtNameValue = tk.Entry(self.groupBox1, width=20)
    #     self.txtNameValue.insert(0, "Value")
    #     self.txtNameValue.grid(row=2, column=1, padx=10, pady=10)

    #     self.opTypeValue = ttk.Combobox(self.groupBox1, values=[
    #         "String", "Binary", "DWORD", "QWORD", "Multi-String", "Expandable String"])
    #     self.opTypeValue.set("Kiểu dữ liệu")
    #     self.opTypeValue.grid(row=2, column=2, padx=10, pady=10)

    #     self.txtKQ = tk.Text(self.groupBox1, height=5, width=60)
    #     self.txtKQ.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    #     self.button1 = tk.Button(
    #         self.groupBox1, text="Gởi", command=button1_click, width=15)
    #     self.button1.grid(row=4, column=0, padx=10, pady=10, sticky=tk.E)

    #     self.butXoa = tk.Button(
    #         self.groupBox1, text="Xóa", command=butXoa_click, width=15)
    #     self.butXoa.grid(row=4, column=2, padx=10, pady=10, sticky=tk.W)

    #     self.root.mainloop()

    #def ScreenshotScene(self):
        # Receive the image size from the server
        #size = int.from_bytes(self.client.recv(4), 'big')
        
        # print("Sending image")
        # filename = r"screenshot.png"
        # with open(filename, 'wb') as fw:
        #     while True:
        #         data = self.client.recv(1024)
        #         if not data:
        #             break
        #         fw.write(data)
        #     fw.close()
        # print("Done")     
        
        # # Receive the image data from the server
        # image_data = b''
        # while len(image_data) < size:
        #     data = self.client.recv(1024)
        #     if not data:
        #         break
        #     image_data += data

        # # Save the image to a file
        # image_path = 'screenshot.jpg'
        # with open(image_path, 'wb') as f:
        #     f.write(image_data)

        # # Open the image using the default image viewer
        # os.startfile(image_path)
        # self.root = tk.Tk()
        # self.root.title("Pic")

        # # Create the picture label
        # self.picture = tk.Label(self.root)
        # self.picture.pack(side=tk.LEFT)

        # # Create the Take button
        # # self.butTake = tk.Button(
        # #     self.root, text="Screenshot", command=self.butTake_click)
        # # self.butTake.pack(side=tk.TOP)

        # # Create the Save button
        # self.button1 = tk.Button(
        #     self.root, text="SAVE", command=self.buttonSAVE_click)
        # self.button1.pack(side=tk.TOP)

    #def butTake_click(self):
        #try:
        #self.client.sendall(b"TAKEPIC")
        # img_size = int.from_bytes(self.recv(4), 'big')
        # img_data = self.recv(img_size)
        # with open(r'D:\screenshot.png', 'wb') as f:
        #     f.write(img_data)
        #     f.close()
        # os.startfile(r'D:\screenshot.png')


        #     #Display screenshot in a new tab
        #     new_tab = ttk.Frame(self.tabs)
        #     tab_label = tk.Label(new_tab)
        #     tab_pil_img = Image.open(io.BytesIO(img_bytes))
        #     tab_img = ImageTk.PhotoImage(tab_pil_img)
        #     tab_label.config(image=tab_img)
        #     tab_label.image = tab_img
        #     tab_label.pack()

        #     save_btn = ttk.Button(
        #         new_tab, text="Save", command=lambda: self.buttonSAVE_click(img_bytes))
        #     save_btn.pack()

        #     self.tabs.add(new_tab, text="Screenshot")      
        # except Exception as ex:
        #     messagebox.showerror("Error", str(ex))

        # while True:
        #     # Receive our data and check what to do with it.
        #     succesful_screenshot = self.recv(4096).decode(encoding="utf-8")
        #     if succesful_screenshot == "returnedScreenshot":
        #         self.settimeout(5.0)
        #         screenshot = b""
        #         chunk = self.recv(4096)
        #         while chunk:
        #             screenshot += chunk
        #             chunk = self.recv(4096)

        #         img = Image.frombytes(data=screenshot, size=(500, 500), mode="RGB")
        #         img.show()

    # def buttonSAVE_click(self, img_bytes):
    #     # Show the save file dialog
    #     filename = filedialog.asksaveasfilename(
    #         title="Save Screenshot",
    #         filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")),
    #         defaultextension=".png"
    #     )
    #     if filename:
    #         with open(filename, 'wb') as f:
    #             f.write(img_bytes)

    # def pic_closing(self):
    #     if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
    #         self.client.sendall(b"EXIT")
    #         self.client.close()

    def run(self):
        self.root.mainloop()  # Start the main event loop
