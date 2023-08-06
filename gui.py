import tkinter as tk
from tkinter import ttk, messagebox
import io
import socket
from PIL import Image, ImageGrab
import pyautogui

HOST = "127.0.1.1"
PORT = 64444


class ScreenshotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Screenshot Tab")
        self.geometry("800x600")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.screenshot_btn = ttk.Button(
            self, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.quit_btn = ttk.Button(self, text="Quit", command=self.close_app)
        self.quit_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        self.Cli_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Cli_Sock.connect((HOST, PORT))

    def take_screenshot(self):
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
                new_tab, text="Save", command=lambda: self.save_screenshot(img_bytes))
            save_btn.pack()

            self.tabs.add(new_tab, text="Screenshot")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def save_screenshot(self, img_bytes):
        filename = tk.filedialog.asksaveasfilename(
            title="Save Screenshot",
            filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")),
            defaultextension=".png"
        )
        if filename:
            with open(filename, 'wb') as f:
                f.write(img_bytes)

    def close_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.Cli_Sock.sendall(b"EXIT")
            self.Cli_Sock.close()
            self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Screenshot App")

    screenshot_btn = ttk.Button(
        root, text="Screenshot")
    screenshot_btn.pack()

    root.mainloop()
