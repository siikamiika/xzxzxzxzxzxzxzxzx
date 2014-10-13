import ctypes
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import string

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


def press_or_release(key):
    if key.endswith('press'):
        do = PressKey
    elif key.endswith('release'):
        do = ReleaseKey
    else: return
    code = ord(key[0].upper())
    if 0x41 <= code <= 0x5A:
        do(code)


with open('index.html') as f:
    index = string.Template(f.read())

class TapHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        press_or_release(self.path[1:])
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        fn = {'/': 'zx.html', '/dfjk': 'dfjk.html'}.get(self.path)
        if fn:
            with open(fn) as f:
                self.wfile.write(index.substitute({'content': f.read()}).encode())

class TapServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ =="__main__":
    srv = TapServer(('', 8001), TapHandler)
    srv.serve_forever()
