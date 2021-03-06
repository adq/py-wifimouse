#!/usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import subprocess
import os
import threading
import SocketServer
import time
import Xlib.keysymdef.miscellany as misckeysyms
import Xlib.keysymdef.xf86 as xf86keysyms
import Xlib.keysymdef.latin1 as latin1keysyms
import Xlib.error
import Xlib.XK
from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input


class ProtocolError(Exception):
    pass

def runcommand(cmd):
    o = open('/dev/null', 'w')
    return subprocess.call(cmd, stdout=o)

keyEventMap = {
    "RTN": misckeysyms.XK_Return,
    "BAS": misckeysyms.XK_BackSpace,
    "TAB": misckeysyms.XK_Tab,
    "SPC": latin1keysyms.XK_space,
    "CAP": misckeysyms.XK_Caps_Lock,
    "NUM_DIVIDE": misckeysyms.XK_KP_Divide,
    "NUM_MULTIPLY": misckeysyms.XK_KP_Multiply,
    "NUM_SUBTRACT": misckeysyms.XK_KP_Subtract,
    "NUM_ADD": misckeysyms.XK_KP_Add,
    "Enter": misckeysyms.XK_KP_Enter,
    "NUM_DECIMAL": misckeysyms.XK_KP_Decimal,
    "NUM0": misckeysyms.XK_KP_0,
    "NUM1": misckeysyms.XK_KP_1,
    "NUM2": misckeysyms.XK_KP_2,
    "NUM3": misckeysyms.XK_KP_3,
    "NUM4": misckeysyms.XK_KP_4,
    "NUM5": misckeysyms.XK_KP_5,
    "NUM6": misckeysyms.XK_KP_6,
    "NUM7": misckeysyms.XK_KP_7,
    "NUM8": misckeysyms.XK_KP_8,
    "NUM9": misckeysyms.XK_KP_9,
    "ESC": misckeysyms.XK_Escape,
    "DELETE": misckeysyms.XK_Delete,
    "HOME": misckeysyms.XK_Home,
    "END": misckeysyms.XK_End,
    "PGUP": misckeysyms.XK_Page_Up,
    "PGDN": misckeysyms.XK_Page_Down,
    "UP": misckeysyms.XK_Up,
    "DW": misckeysyms.XK_Down,
    "RT": misckeysyms.XK_Right,
    "LF": misckeysyms.XK_Left,
    "F1": misckeysyms.XK_F1,
    "F2": misckeysyms.XK_F2,
    "F3": misckeysyms.XK_F3,
    "F4": misckeysyms.XK_F4,
    "F5": misckeysyms.XK_F5,
    "F6": misckeysyms.XK_F6,
    "F7": misckeysyms.XK_F7,
    "F8": misckeysyms.XK_F8,
    "F9": misckeysyms.XK_F9,
    "F10": misckeysyms.XK_F10,
    "F11": misckeysyms.XK_F11,
    "F12": misckeysyms.XK_F12,
    "CTRL": misckeysyms.XK_Control_L,
    "ALT": misckeysyms.XK_Alt_L,
    "SHIFT": misckeysyms.XK_Shift_L,
    "VOLUMEDN": xf86keysyms.XK_XF86_AudioLowerVolume,
    "VOLUMEUP": xf86keysyms.XK_XF86_AudioRaiseVolume,
    "MUTE": xf86keysyms.XK_XF86_AudioMute,
}


def x11Key(display, state, raw):
    if type(raw) in (str, unicode):
        keysym = keyEventMap.get(raw)
        if keysym is None:
            try:
                keysym = ord(raw)
            except TypeError:
                raise ProtocolError('Unknown x11 key {}'.format(raw))
    else:
        keysym = raw

    keycodes = display.keysym_to_keycodes(keysym)
    if len(keycodes) == 0:
        return
    keycode = keycodes[0]

    if 'down' in state:
        if keycode[1] == 1:  # ie this keycode is in modmap group 2, which means shift needs to be pressed... yuck, X keyboard sucks!
            fake_input(display, X.KeyPress, detail=display.keysym_to_keycode(misckeysyms.XK_Shift_L))
            display.sync()

        fake_input(display, X.KeyPress, detail=keycode[0])
        display.sync()

    if 'up' in state:
        fake_input(display, X.KeyRelease, detail=keycode[0])
        display.sync()

        if keycode[1] == 1:
            fake_input(display, X.KeyRelease, detail=display.keysym_to_keycode(misckeysyms.XK_Shift_L))
            display.sync()


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
            raise ProtocolError("Unknown mouse button {}".format(bits[1]))

        if bits[2] == 'd':
            xevent = X.ButtonPress
        elif bits[2] == 'u':
            xevent = X.ButtonRelease
        else:
            raise ProtocolError("Unknown mouse action {}".format(bits[2]))

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
        raise ProtocolError("Unknown mouse event {}".format(arg))


def keyEvent(display, eventname, event, arg):
    if arg.startswith('[R]'):
        bits = arg[4:].split(' ')
        raw = bits[0]

        if bits[1] == 'd':
            state = 'down'
        elif bits[1] == 'u':
            state = 'up'
        else:
            raise ProtocolError('Unknown keyevent state {}'.format(arg))

    else:
        raw = arg
        state = 'downup'

    x11Key(display, state, raw)


def dragEvent(display, eventname, event, arg):
    if arg == 'start':
        fake_input(display, X.ButtonPress, detail=X.Button1)
        display.sync()

    elif arg == 'end':
        fake_input(display, X.ButtonRelease, detail=X.Button1)
        display.sync()

    else:
        bits = arg.split(' ')
        x = int(bits[1])
        y = int(bits[2])
        fake_input(display, X.MotionNotify, x=x, y=y, detail=1)  # detail=1 => relative motion event
        display.sync()


def utf8Event(display, eventname, event, arg):
    arg = arg.decode('utf-8')
    for k in arg:
        x11Key(display, 'downup', k)


def slideEvent(display, eventname, event, arg):
    if arg == ' begin':
        x11Key(display, 'down', misckeysyms.XK_Alt_L)

    elif arg == 'left':
        x11Key(display, 'up', misckeysyms.XK_Shift_L)
        x11Key(display, 'downup', misckeysyms.XK_Tab)

    elif arg == 'right':
        x11Key(display, 'down', misckeysyms.XK_Shift_L)
        x11Key(display, 'downup', misckeysyms.XK_Tab)

    elif arg == ' end':
        x11Key(display, 'up', misckeysyms.XK_Shift_L)
        x11Key(display, 'up', misckeysyms.XK_Alt_L)

    else:
        raise ProtocolError("Unknown slide command {}".format(arg))


def powerEvent(display, eventname, event, arg):
    print("Power command {}".format(eventname))


def cmdtableEvent(display, eventname, event, arg):
    keyseq = event['cmdtable'].get(arg)
    if keyseq is None:
        raise ProtocolError("Unknown cmdtable command: {}/{}".format(event, arg))

    for k in keyseq:
        x11Key(display, 'down', k)
    for k in reversed(keyseq):
        x11Key(display, 'up', k)


def hardkeyEvent(display, eventname, event, arg):
    x11Key(display, 'downup', eventname.upper())


def windowEvent(display, eventname, event, arg):
    if arg == 'minimize':
        pass

    elif arg == 'maximize':
        pass

    elif arg == 'close':
        pass

    else:
        raise ProtocolError("Unknown window command {}".format(arg))


def browserEvent(display, eventname, event, arg):
    if arg == 'forward':
        pass

    elif arg == 'back':
        pass

    elif arg == 'home':
        pass

    elif arg == 'search':
        pass

    elif arg == 'refresh':
        pass

    elif arg == 'stop':
        runcommand(['pkill', '-9', 'pluginloader'])

    elif arg == 'favorite':
        pass

    elif arg == 'newtab':
        pass

    else:
        raise ProtocolError("Unknown browser command {}".format(arg))


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
    'in': [misckeysyms.XK_Control_L, '+'],
    'out': [misckeysyms.XK_Control_L, '-'],
}

events = {
    'mos': {'fn': mouseEvent, 'term': 'length'},
    'key': {'fn': keyEvent, 'term': 'length'},
    'drag': {'fn': dragEvent, 'skip': 1, 'term': 'nl'},
    'utf8': {'fn': utf8Event, 'skip': 1, 'term': 'nl'},
    'slide': {'fn': slideEvent, 'term': 'nl'},

    'media': {'cmdtable': mediaCommands, 'skip': 1, 'term': 'nl'},
    'zoom': {'cmdtable': zoomCommands, 'term': 'nl'},
    'browser': {'fn': browserEvent, 'skip': 1, 'term': 'nl'},
    'window': {'fn': windowEvent, 'skip': 1, 'term': 'nl'},
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

            arg = arg[event.get('skip', 0):]

            if 'cmdtable' in event:
                cmdtableEvent(display, eventname, event, arg)

            elif 'fn' in event:
                event['fn'](display, eventname, event, arg)

        if not ok:  # we failed to parse the command...
            # if there's more than 20 chars, its probably an unknown command. Log it. Otherwise, its likely a
            # partial buffer, so leave the buf alone to be prepended onto the next processing loop.
            if len(buf) > 20:
                raise ProtocolError("Unknown command {}".format(buf))
                buf = ''
            break

    return buf


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        print "HOO"
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

            except ProtocolError, ex:
                print ex


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
