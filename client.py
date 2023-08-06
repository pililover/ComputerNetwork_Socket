import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
import subprocess

HOST = "127.0.1.1"
PORT = 64444


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.Cli_Sock = None
        self.network_file = None

    def connect(self, ip):
        """Connect to the server."""
        try:
            self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Cli_Sock.connect((ip, self.port))
            self.network_file = self.Cli_Sock.makefile('rw')
            messagebox.showinfo(
                "Connected", "Connected to the server successfully")
        except socket.error as ex:
            messagebox.showerror(
                "Error", f"Failed to connect to the server: {ex}")
            self.Cli_Sock = None
            self.network_file = None

    def send_command(self, command):
        """Send a command to the server."""
        if self.Cli_Sock is None:
            messagebox.showerror("Error", "Not connected to the server")
            return
        try:
            self.network_file.write(command + "\n")
            self.network_file.flush()
        except socket.timeout as ex:
            messagebox.showerror(
                "Error", f"Timeout while sending command to the server: {ex}")
        except socket.error as ex:
            messagebox.showerror(
                "Error", f"Failed to send command to the server: {ex}")

    def handle_response(self, res):
        """Handle the response from the server based on the response type."""
        # Add code to handle different types of responses from the server
        pass

    def app_click(self):
        """Send the APPLICATION command to the server and handle the response."""
        self.send_command("APPLICATION")
        # handle_response("APPLICATION")

    def shutdown_click(self):
        """Send the SHUTDOWN command to the server and handle the response."""
        self.send_command("SHUTDOWN")
        # handle_response("SHUTDOWN")

    def registry_click(self):
        """Send the REGISTRY command to the server and handle the response."""
        self.send_command("REGISTRY")
        # handle_response("REGISTRY")

    def exit_click(self):
        """Send the QUIT command to the server, close the connection, and exit the application."""
        if not messagebox.askokcancel("Quit", "Do you want to quit?"):
            return

        if (self.Cli_Sock is not None):
            try:
                # Send QUIT command to server
                self.send_command("QUIT")
                # Close socket connection
                self.Cli_Sock.close()
            except:
                pass

    def pic_click(self):
        """Send the TAKEPIC command to the server and handle the response."""
        self.send_command("TAKEPIC")
        # handle_response("TAKEPIC")

    def key_lock_click(self):
        """Send the KEYLOG command to the server and handle the response."""
        self.send_command("KEYLOG")
        # handle_response("KEYLOG")

    def process_click(self):
        """Send the PROCESS command to the server and handle the response."""
        self.send_command("PROCESS")
        # handle_response("PROCESS")

    
def blank():
    root=tk.Tk()
    text=tk.Label(root, text="This is a blanked scene!")
    text.pack(padx=20, pady = 20)
    
    root.mainloop()
    
# Create the main GUI window
class GUI:
    def __init__(self, client):
        self.client = client
    
    
    def clientScene(self):
        root = tk.Tk()
        root.title("Client")
        # Input Box
        text = tk.Label(root, text="Enter IP:")
        text.grid (row=0, column=0, pady=10)
        
        inputBox = tk.Entry(root, width = 50)
        inputBox.grid (row = 0, column = 1, columnspan=3, pady=10)
                
        def connect_wrapper():
            ip = inputBox.get()
            self.client.connect(ip)
            
        # Connect Button
        connectButt = tk.Button(root, text="Connect", width=10, command=connect_wrapper) 
        connectButt.grid (row = 0, column=6, padx = 10, pady =10)
        
        # Process Running
        processButt = tk.Button(root, text="Process Running", padx = 20, pady = 20, command=self.client.process_click)
        processButt.grid (row = 1, column=0, padx=40, pady=10, columnspan=2)
        
        # Application Running
        appButt = tk.Button(root, text="App Running", padx = 30, pady = 20, command=self.client.app_click)
        appButt.grid(row=1, column=2, pady=10)
        
        #Shut Down
        shutDownButt = tk.Button(root, text="Shut Down", padx=35, pady= 20, command=self.client.shutdown_click)
        shutDownButt.grid(row=2, column=0,padx=40, pady=10, columnspan=2)
        
        # Screenshot
        screenShotButt = tk.Button(root, text="Screenshot", padx=34, pady=20, command=self.client.pic_click)
        screenShotButt.grid(row = 2, column=2, pady=10)
        
        # Keystroke
        keyStrokeButt = tk.Button(root, text="Keystroke", padx = 39, pady=20, command=self.client.key_lock_click)
        keyStrokeButt.grid(row=3, column=0, padx=40, pady =10, columnspan=2)
        
        # Registry
        registryButt = tk.Button(root, text="Edit Registry", padx = 33, pady=20, command=self.client.registry_click)
        registryButt.grid(row=3, column=2, pady =10)
        
        # Exit
        exit = tk.Button(root, text="Quit", bg="red", padx = 30, pady = 10, command = self.client.exit_click)
        exit.grid(row=2, column=6, padx = 10, pady = 20)
    
        root.mainloop()
        
    def processScene(self):
        process_window = tk.Tk()
        process_window.title("Process")

        def kill_click():
            # Implement the kill action
            pass

        def view_click():
            # Implement the view action
            pass

        def start_click():
            # Implement the start action
            pass

        def delete_click():
            # Implement the delete action
            pass

        # Buttons
        kill_button = tk.Button(process_window, text="Kill", width=10, command=kill_click)
        kill_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = tk.Button(process_window, text="Xem", width=10, command=view_click)
        view_button.grid(row=0, column=1, padx=10, pady=10)

        delete_button = tk.Button(process_window, text="Xóa", width=10, command=delete_click)
        delete_button.grid(row=0, column=2, padx=10, pady=10)

        start_button = tk.Button(process_window, text="Start", width=10, command=start_click)
        start_button.grid(row=0, column=3, padx=10, pady=10)

        # TreeView
        process_list = ttk.Treeview(process_window, columns=("Name Process", "ID Process", "Count Thread"), show="headings")
        process_list.heading("#1", text="Name Process")
        process_list.heading("#2", text="ID Process")
        process_list.heading("#3", text="Count Thread")
        process_list.grid(row=1, column=0, columnspan=4, padx=20, pady=20)

        process_window.mainloop()

# Create a Client instance
client = Client(HOST, PORT)

# Create a GUI instance and pass in the client
gui = GUI(client)
gui.clientScene()

# Show the process scene (added step)
gui.processScene()
# Start the main event loop
# gui.root.mainloop()