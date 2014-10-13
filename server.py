import ctypes
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# ctypes code thanks http://stackoverflow.com/a/13615802/2444105

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( hexKeyCode, 0x48, 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def x_press():
    PressKey(0x58)

def x_release():
    ReleaseKey(0x58)

def z_press():
    PressKey(0x5a)

def z_release():
    ReleaseKey(0x5a)


with open('index.html', 'rb') as f:
    index = f.read()

class TapHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/x_press':
            Thread(target=x_press).start()
        elif self.path == '/x_release':
            Thread(target=x_release).start()
        elif self.path == '/z_press':
            Thread(target=z_press).start()
        elif self.path == '/z_release':
            Thread(target=z_release).start()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        if self.path == '/':
            self.wfile.write(index)


if __name__ =="__main__":
    srv = HTTPServer(('', 8001), TapHandler)
    srv.serve_forever()
