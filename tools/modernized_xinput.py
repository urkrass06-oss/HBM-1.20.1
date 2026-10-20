#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Send local XTest input to the explicitly selected DISPLAY for Minecraft tests."""

import argparse
import ctypes
import os
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("click", "right", "move", "key", "text", "selectall"))
    parser.add_argument("values", nargs="*")
    args = parser.parse_args()
    x = ctypes.CDLL("libX11.so.6")
    test = ctypes.CDLL("libXtst.so.6")
    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x.XOpenDisplay.restype = ctypes.c_void_p
    display = x.XOpenDisplay(os.environ.get("DISPLAY", "").encode())
    if not display:
        raise SystemExit("Set DISPLAY to the local test X server")
    x.XStringToKeysym.argtypes = [ctypes.c_char_p]
    x.XStringToKeysym.restype = ctypes.c_ulong
    x.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x.XKeysymToKeycode.restype = ctypes.c_uint
    x.XkbKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int]
    x.XkbKeycodeToKeysym.restype = ctypes.c_ulong
    x.XFlush.argtypes = [ctypes.c_void_p]
    x.XCloseDisplay.argtypes = [ctypes.c_void_p]
    test.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    test.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    test.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]

    def key(symbol, pressed):
        test.XTestFakeKeyEvent(display, x.XKeysymToKeycode(display, symbol), pressed, 0)

    def tap(symbol):
        key(symbol, 1)
        key(symbol, 0)
        x.XFlush(display)
        time.sleep(0.08)

    try:
        if args.action in ("click", "right", "move"):
            if len(args.values) != 2:
                parser.error("Pointer actions require X Y")
            test.XTestFakeMotionEvent(display, 0, int(args.values[0]), int(args.values[1]), 0)
            if args.action != "move":
                button = 3 if args.action == "right" else 1
                test.XTestFakeButtonEvent(display, button, 1, 0)
                test.XTestFakeButtonEvent(display, button, 0, 0)
        elif args.action == "selectall":
            control = x.XStringToKeysym(b"Control_L")
            key(control, 1)
            tap(ord("a"))
            key(control, 0)
        elif args.action == "key":
            tap(x.XStringToKeysym(args.values[0].encode()))
        elif args.action == "text":
            shift = x.XStringToKeysym(b"Shift_L")
            for char in args.values[0]:
                symbol = ord(char)
                code = x.XKeysymToKeycode(display, symbol)
                shifted = x.XkbKeycodeToKeysym(display, code, 0, 0) != symbol
                if shifted:
                    key(shift, 1)
                tap(symbol)
                if shifted:
                    key(shift, 0)
        x.XFlush(display)
    finally:
        x.XCloseDisplay(display)


if __name__ == "__main__":
    main()
