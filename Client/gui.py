# gui.py
import tkinter as tk
from tkinter import ttk, messagebox

img_bytes = b'\x00\x01\x02...'



class GUI:
    def __init__(self, client, data):
        self.client = client
        if data == "APPLICATION":
            self.appScene()
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
        
    def killScene(self):
        kill_scene = tk.Tk()
        kill_scene.title("kill")
        text = tk.Label(kill_scene, text="Enter PID:")
        text.grid(row=0, column=0, padx=10, pady=10)
        inputBox = tk.Entry(kill_scene, width=30)
        inputBox.grid(row=0, column=1,pady=10)
        
        def clicked():
            self.kill_app(inputBox.get())
        
        connectButt = tk.Button(kill_scene, text="Kill",
                                width=10, command=clicked)
        connectButt.grid(row=0, column=2, padx=10, pady=10)
        
        kill_scene.mainloop()
    
    def start_app(self, app_name):
        try:
            self.client.Cli_Sock.send(f"start {app_name}".encode())
            response = self.client.Cli_Sock.recv(1024).decode()
            messagebox.showinfo("Response", response)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            
    def kill_app(self, pid):
        try:
            self.client.Cli_Sock.send(f"kill {pid}".encode())
            response = self.client.Cli_Sock.recv(1024).decode()
            messagebox.showinfo("Response", response)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
    
    def processScene(self):
        # process_window = Process(self.client)
        # process_window.mainloop()
        process_window = tk.Tk()
        process_window.title("Process")
        
        def quit_signal():
            self.client.Cli_Sock.send("QUIT".encode())
            process_window.destroy()
        
        def kill_click():
            self.killScene()
            
        def view_click():
            try:
                self.client.Cli_Sock.send("view".encode()) # Send the command to the server
                response = self.client.Cli_Sock.recv(4096).decode()  # Increased buffer size for more data
                print(response)
                for item in self.process_list.get_children():
                    self.process_list.delete(item)
                for line in response.split("\n"):
                    columns = line.split("\t")
                    if len(columns) == 3:  # Expecting three columns: Image name, PID, Thread count
                        self.process_list.insert("", "end", values=columns)
                messagebox.showinfo("Response", response)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
        
        def start_click():
            self.startScene()
            
        def delete_click():
            for item in self.process_list.get_children():
                self.process_list.delete(item)

        process_window.protocol("WM_DELETE_WINDOW", quit_signal)
                
        self.process_list = ttk.Treeview(process_window, columns=(
            "Name process", "ID process", "Count Thread"), show="headings")
        self.process_list.heading("#1", text="Name process")
        self.process_list.heading("#2", text="ID process")
        self.process_list.heading("#3", text="Count Thread")
        self.process_list.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        # Buttons
        kill_button = tk.Button(process_window, text="Kill",
                                width=10, command=kill_click)
        kill_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(process_window, text="View",
                                width=10, command=view_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        start_button = tk.Button(
            process_window, text="Start", width=10, command=start_click)
        start_button.grid(row=0, column=2, padx=10, pady=10)
        
        delete_button = tk.Button(
            process_window, text="Delete", width=10, command=delete_click) 
        delete_button.grid(row=0, column=3, padx=10, pady=10)

        process_window.mainloop()

    def appScene(self):

        app_window = tk.Tk()
        app_window.title("App")

        def quit_signal():
            self.client.Cli_Sock.send("QUIT".encode())
            app_window.destroy()

        def kill_click():
            self.killScene()

        def view_click():
            try:
                self.client.Cli_Sock.send("view".encode()) # Send the command to the server
                response = self.client.Cli_Sock.recv(4096).decode()  # Increased buffer size for more data
                print(response)
                for item in self.app_list.get_children():
                    self.app_list.delete(item)
                for line in response.split("\n"):
                    columns = line.split("\t")
                    if len(columns) == 3:  # Expecting three columns: Image name, PID, Thread count
                        self.app_list.insert("", "end", values=columns)
                messagebox.showinfo("Response", response)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def start_click():
            self.startScene()
                

        def delete_click():
            for item in self.app_list.get_children():
                self.app_list.delete(item)
            
        app_window.protocol("WM_DELETE_WINDOW", quit_signal)

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

        def hook_click():
            self.client.Cli_Sock.send("HOOK".encode()) # Send the command to the server

        def unhook_click():
            self.client.Cli_Sock.send("UNHOOK".encode())

        def print_click():
            self.client.Cli_Sock.send("PRINT".encode())
            data = self.client.Cli_Sock.recv(5000).decode()
            print (data)
            self.txtKQ.insert(tk.END, data)

        def delete_click():
            self.client.Cli_Sock.send("CLEAR".encode())
            self.txtKQ.delete("1.0", tk.END)
            
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

        key_window.mainloop()

    def run(self):
        self.root.mainloop()  # Start the main event loop
