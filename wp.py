# whatsapp_switcher.py

import time
import urllib.parse
import webbrowser
import sys
import os
import argparse

# — try to import window/control libs, else prompt to install —
try:
    import pygetwindow as gw
    import pyautogui
    import win32process
    import psutil
except ImportError:
    print("⚠️  Missing dependencies. Install with:\n    pip install pygetwindow pyautogui pywin32 psutil")
    sys.exit(1)

# Only treat these executables as valid WhatsApp Web hosts
BROWSERS = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"}

def is_whatsapp_web_window(win):
    """Detect a browser window/tab running WhatsApp Web."""
    if not (win.visible and "WhatsApp" in win.title):
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(win._hWnd)
        exe = psutil.Process(pid).name().lower()
    except Exception:
        return False
    return exe in BROWSERS

def is_whatsapp_desktop_window(win):
    """Detect the native WhatsApp Desktop window."""
    if not (win.visible and "WhatsApp" in win.title):
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(win._hWnd)
        exe = psutil.Process(pid).name().lower()
    except Exception:
        return False
    return exe == "whatsapp.exe"

def send_via_web(chat_id: str, message: str, idx: int):
    """Send via WhatsApp Web by opening the URL in-browser and automating paste+enter."""
    encoded = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={chat_id}&text={encoded}"

    # focus existing tab or open new one
    wa_tabs = [w for w in gw.getAllWindows() if is_whatsapp_web_window(w)]
    if wa_tabs:
        win = wa_tabs[0]
        win.activate()
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.typewrite(url)
        pyautogui.press("enter")
    else:
        webbrowser.open_new_tab(url)

    # initial load wait
    time.sleep(5 if idx == 1 else 2)
    pyautogui.press("enter")

def send_via_desktop(chat_id: str, message: str, idx: int):
    """Send via WhatsApp Desktop using the whatsapp:// URI scheme."""
    encoded = urllib.parse.quote(message)
    uri = f"whatsapp://send?phone={chat_id}&text={encoded}"

    # try launching the desktop app
    try:
        os.startfile(uri)
    except Exception:
        # fallback: open in default browser
        webbrowser.open(uri)

    # wait for the app to open
    time.sleep(5 if idx == 1 else 2)

    # find and focus the Desktop window
    wa_windows = [w for w in gw.getAllWindows() if is_whatsapp_desktop_window(w)]
    if wa_windows:
        win = wa_windows[0]
        win.activate()
        time.sleep(0.5)

    pyautogui.press("enter")

def send_whatsapp(chat_id: str, message: str, idx: int, mode: str = "auto"):
    """Dispatch to the selected mode (web, desktop, or auto)."""
    if mode == "web":
        send_via_web(chat_id, message, idx)
    elif mode == "desktop":
        send_via_desktop(chat_id, message, idx)
    elif mode == "auto":
        try:
            send_via_desktop(chat_id, message, idx)
        except Exception:
            send_via_web(chat_id, message, idx)
    else:
        raise ValueError(f"Unknown mode '{mode}'. Choose from 'web', 'desktop', or 'auto'.")

if __name__ == "__main__":

    # Map each phone number to a name
    recipients = {
        "201093553466":"Omar",
        # add more recipients here…
    }

    total = len(recipients)
    for idx, (number, name) in enumerate(recipients.items(), start=1):
        print(f"\n➡️  Sending to {name} ({number}) — {idx}/{total}")
        message = f"Hello {name}! This is your message #{idx} of {total}."
        if number.startswith("0"):
            number = "2" + number  # ensure country code

        send_whatsapp(number, message, idx, mode="desktop")
        time.sleep(5)
