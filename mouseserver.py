#!/usr/bin/python2

import socket
import os
import threading
import SocketServer
import time
import Xlib.keysymdef.miscellany as xkeysyms
import Xlib.keysymdef.xf86 as xf86keysyms
import Xlib.error
from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input


keycodes = {
    "RTN": xkeysyms.XK_Return,
    "BAS": xkeysyms.XK_BackSpace,
    "TAB": xkeysyms.XK_Tab,
    "SPC": ' ',
    " ": ' ',
    "CAP": xkeysyms.XK_Caps_Lock,
    "a": 'a',
    "0": '0',
    "1": '1',
    "2": '2',
    "3": '3',
    "4": '4',
    "5": '5',
    "6": '6',
    "7": '7',
    "8": '8',
    "9": '9',
    "-": '-',
    "=": '=',
    "`": '`',
    ".": '.',
    ",": ',',
    ":": ':',
    "\"": '"',
    "/": '/',
    "b": 'b',
    "c": 'c',
    "d": 'd',
    "e": 'e',
    "f": 'f',
    "g": 'g',
    "h": 'h',
    "i": 'i',
    "j": 'j',
    "k": 'k',
    "l": 'l',
    "m": 'm',
    "n": 'n',
    "o": 'o',
    "p": 'p',
    "q": 'q',
    "r": 'r',
    "s": 's',
    "t": 't',
    "u": 'u',
    "v": 'v',
    "w": 'w',
    "x": 'x',
    "y": 'y',
    "z": 'z',

    "?": 63,
    "!": '!',
    "'": '\'',
    "@": '@',
    "+": '+',
    "-": '-',
    "*": '*',
    "/": '/',
    "\"": '"',
    ";": ';',
    "&": '&',
    ":": ':',
    "#": '#',
    "(": '(',
    ")": ')',
    "%": '%',
    "$": '$',
    "~": '~',
    "[": '[',
    "]": ']',
    "\\": '\\',
    "|": '|',
    "{": '{',
    "}": '}',
    "<": '<',
    ">": '>',
    "_": '_',

    "NUM_DIVIDE": xkeysyms.XK_KP_Divide,
    "NUM_MULTIPLY": xkeysyms.XK_KP_Multiply,
    "NUM_SUBTRACT": xkeysyms.XK_KP_Subtract,
    "NUM_ADD": xkeysyms.XK_KP_Add,
    "Enter": xkeysyms.XK_KP_Enter,
    "NUM_DECIMAL": xkeysyms.XK_KP_Decimal,
    "NUM0": xkeysyms.XK_KP_0,
    "NUM1": xkeysyms.XK_KP_1,
    "NUM2": xkeysyms.XK_KP_2,
    "NUM3": xkeysyms.XK_KP_3,
    "NUM4": xkeysyms.XK_KP_4,
    "NUM5": xkeysyms.XK_KP_5,
    "NUM6": xkeysyms.XK_KP_6,
    "NUM7": xkeysyms.XK_KP_7,
    "NUM8": xkeysyms.XK_KP_8,
    "NUM9": xkeysyms.XK_KP_9,

    "ESC": xkeysyms.XK_Escape,
    "DELETE": xkeysyms.XK_Delete,
    "HOME": xkeysyms.XK_Home,
    "END": xkeysyms.XK_End,
    "PGUP": xkeysyms.XK_Page_Up,
    "PGDN": xkeysyms.XK_Page_Down,
    "UP": xkeysyms.XK_Up,
    "DW": xkeysyms.XK_Down,
    "RT": xkeysyms.XK_Right,
    "LF": xkeysyms.XK_Left,
    "F1": xkeysyms.XK_F1,
    "F2": xkeysyms.XK_F2,
    "F3": xkeysyms.XK_F3,
    "F4": xkeysyms.XK_F4,
    "F5": xkeysyms.XK_F5,
    "F6": xkeysyms.XK_F6,
    "F7": xkeysyms.XK_F7,
    "F8": xkeysyms.XK_F8,
    "F9": xkeysyms.XK_F9,
    "F10": xkeysyms.XK_F10,
    "F11": xkeysyms.XK_F11,
    "F12": xkeysyms.XK_F12,
    "CTRL": xkeysyms.XK_Control_L,
    "ALT": xkeysyms.XK_Alt_L,
    "SHIFT": xkeysyms.XK_Shift_L,

    "VOLUMEDN": xf86keysyms.XK_XF86_AudioLowerVolume,
    "VOLUMEUP": xf86keysyms.XK_XF86_AudioRaiseVolume,
    "MUTE": xf86keysyms.XK_XF86_AudioMute,
}


def mouseEvent(display, eventname, event, arg):
    bits = arg.split(' ')
    if bits[0] == 'm':
        x = int(bits[1])
        y = int(bits[2])

        fake_input(display, X.MotionNotify, x=x, y=y, detail=1)  # detail=1 => relative motion event
        display.sync()

    elif bits[0] == 'R':
        if bits[1] == 'l':
            xbutton = X.Button1
        elif bits[1] == 'm':
            xbutton = X.Button2
        elif bits[1] == 'r':
            xbutton = X.Button3
        else:
            raise Exception("Unknown mouse button {}".format(bits[1]))

        if bits[2] == 'd':
            xevent = X.ButtonPress
        elif bits[2] == 'u':
            xevent = X.ButtonRelease
        else:
            raise Exception("Unknown mouse action {}".format(bits[2]))

        fake_input(display, xevent, detail=xbutton)
        display.sync()

    elif bits[0] == 'c':
        fake_input(display, X.ButtonPress, detail=X.Button1)
        display.sync()
        fake_input(display, X.ButtonRelease, detail=X.Button1)
        display.sync()

    elif bits[0] == 'w':
        offset = int(bits[1])
        if offset > 0:
            xbutton = X.Button5
        else:
            xbutton = X.Button4

        fake_input(display, X.ButtonPress, detail=xbutton)
        display.sync()
        fake_input(display, X.ButtonRelease, detail=xbutton)
        display.sync()

    else:
        raise Exception("Unknown mouse event {}".format(arg))


def keyEvent(display, eventname, event, arg):
    if arg.startswith('[R]'):
        bits = arg[4:].split(' ')
        keys = keycodes.get(bits[0])

        state = None
        if bits[1] == 'd':
            state = 'down'
        elif bits[1] == 'u':
            state = 'up'

        if keys is not None:
            print("KEY {} {}".format(keys, state))

    else:
        keys = keycodes.get(arg)
        print("KEY {}".format(keys))


def dragEvent(display, eventname, event, arg):
    if arg == 'start':
        print("DRAG START")
    elif arg == 'end':
        print("DRAG END")
    else:
        bits = arg.split(' ')
        print("DRAG {} {}".format(int(bits[0]), int(bits[1])))


def utf8Event(display, eventname, event, arg):
    for k in arg:
        print("UTF8 {}".format(k))


def powerEvent(display, eventname, event, arg):
    print("Power command {}".format(eventname))


def cmdtableEvent(display, eventname, event, arg):
    keys = event['cmdtable'].get(arg)
    if keys is None:
        print("Unknown command: {}/{}".format(event, arg))
    else:
        print("Command: {}/{}".format(eventname, arg))


def hardkeyEvent(display, eventname, event, arg):
    keys = keycodes.get(eventname.upper())
    if keys is None:
        print("Unknown command: {}".format(eventname))
    else:
        print("Hardkey Command: {}".format(eventname))


browserCommands = {
    'forward': [xkeysyms.XK_Alt_L, xkeysyms.XK_Right],
    'back': [xkeysyms.XK_Alt_L, xkeysyms.XK_Left],
    'home': [xkeysyms.XK_Alt_L, xkeysyms.XK_Home],
    'search': [xkeysyms.XK_Control_L, 'k'],
    'refresh': [xkeysyms.XK_Control_L, 'r'],
    'stop': [xkeysyms.XK_Escape],
    'favorite': [xkeysyms.XK_Control_L, 'b'],
    'newtab': [xkeysyms.XK_Control_L, 't'],
}

windowCommands = {
    'minimize': [],  # FIXME
    'maximize': [],  # FIXME
    'close': [],  # FIXME
}

pptCommands = {
    'pgup': [],  # FIXME
    'play': [],  # FIXME
    'pgdn': [],  # FIXME
    'stop': [],  # FIXME
    'run': [],  # FIXME
    'exit': [],  # FIXME
    'switch': [],  # FIXME
}

mediaCommands = {
    'play': [xf86keysyms.XK_XF86_AudioPlay],
    'next': [xf86keysyms.XK_XF86_AudioNext],
    'prev': [xf86keysyms.XK_XF86_AudioPrev],
    'volumeup': [xf86keysyms.XK_XF86_AudioRaiseVolume],
    'volumedown': [xf86keysyms.XK_XF86_AudioLowerVolume],
}

zoomCommands = {
    'in': [xkeysyms.XK_Control_L, '+'],
    'out': [xkeysyms.XK_Control_L, '-'],
}

slideCommands = {
    ' begin': [],  # leading space intentional
    'left': [],
    'right': [],
    ' end': [],  # leading space intentional
}

events= {'mos': {'fn': mouseEvent, 'term': 'length'},
         'key': {'fn': keyEvent, 'term': 'length'},
         'drag': {'fn': dragEvent, 'skip': 1, 'term': 'nl'},
         'utf8': {'fn': utf8Event, 'skip': 1, 'term': 'nl'},
         'slide': {'cmdtable': slideCommands, 'term': 'nl'},

         'media': {'cmdtable': mediaCommands, 'skip': 1, 'term': 'nl'},
         'zoom': {'cmdtable': zoomCommands, 'term': 'nl'},
         'browser': {'cmdtable': browserCommands, 'skip': 1, 'term': 'nl'},
         'window': {'cmdtable': windowCommands, 'skip': 1, 'term': 'nl'},
         'ppt': {'cmdtable': pptCommands, 'skip': 1, 'term': 'nl'},

         'logoff': {'fn': powerEvent, 'term': 'nl'},
         'sleep': {'fn': powerEvent, 'term': 'nl'},
         'poweroff': {'fn': powerEvent, 'term': 'nl'},
         'reboot': {'fn': powerEvent, 'term': 'nl'},
         'shutdown': {'fn': powerEvent, 'term': 'nl'},

         'mute': {'fn': hardkeyEvent, 'term': 'nl'},
         'volumedn': {'fn': hardkeyEvent, 'term': 'nl'},
         'volumeup': {'fn': hardkeyEvent, 'term': 'nl'},
         'rtn': {'fn': hardkeyEvent, 'term': 'nl'},
         'bas': {'fn': hardkeyEvent, 'term': 'nl'},
         }

def process(buf, display):
    while len(buf):
        lowerbuf = buf.lower()
        ok = False
        for eventname, event in events.iteritems():
            if not lowerbuf.startswith(eventname):
                continue
            ok = True

            if event['term'] == 'nl':
                nlidx = buf.index('\n')
                if nlidx < 0:
                    return buf
                arg = buf[len(eventname):nlidx]
                buf = buf[nlidx+1:]

            elif event['term'] == 'length':
                skip = len(eventname)
                if len(buf) < skip + 3:
                    return buf
                l = int(buf[skip:skip+3])
                if len(buf) < skip + 3 + l:
                    return buf
                arg = buf[skip+3:skip+3+l]
                buf = buf[skip+3+l:]

            if 'skip' in event:
                arg = arg[event['skip']:]

            if 'cmdtable' in event:
                cmdtableEvent(display, eventname, event, arg)

            elif 'fn' in event:
                event['fn'](display, eventname, event, arg)

        if not ok:  # we failed to parse the command...
            # if there's more than 20 chars, its probably an unknown command. Log it. Otherwise, its likely a
            # partial buffer, so leave the buf alone to be prepended onto the next processing loop.
            if len(buf) > 20:
                print("Unknown command {}".format(buf))
                buf = ''
            break

    return buf


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        display = None
        self.request.send('Linux!')

        oldbuf= ''
        while True:
            buf = oldbuf + self.request.recv(1024)
            oldbuf = ''

            if display is None:
                try:
                    display = Display(display=':0')
                except:
                    continue

            try:
                oldbuf = process(buf, display)

            except Xlib.error.ConnectionClosedError:
                # ok, just ignore these -- X closed underneath us, so just keep going until it reappears
                display = None


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    # set HOME to something if it isn't already
    if 'HOME' not in os.environ:
        os.environ['HOME'] = 'root'

    # start a tcp server socket
    server = ThreadedTCPServer(('0.0.0.0', 1978), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.daemon_threads = True
    server_thread.start()

    # broadcast we're here over UDP!
    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    udpmsg = 'BC{:3}{}'.format(len(socket.gethostname()), socket.gethostname())
    while True:
        try:
            udpsock.sendto(udpmsg, ('255.255.255.255', 2008))
        except socket.error:
            pass
        time.sleep(1)
    server.shutdown()
