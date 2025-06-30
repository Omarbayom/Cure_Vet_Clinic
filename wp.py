# wp.py

import time
import urllib.parse
import webbrowser
import sys
import os
import win32gui, win32con
import ctypes




# — try to import window/control libs —
try:
    import pygetwindow as gw
    import pyautogui
    import win32process
    import psutil
    import pyperclip
except ImportError as e:
    raise ImportError(
        "Missing dependencies for wp module: "
        "pip install pygetwindow pyautogui pywin32 psutil pyperclip"
    ) from e

# Only these executables count as valid WhatsApp Web hosts
BROWSERS = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"}

def is_whatsapp_web_window(win) -> bool:
    """Detect a browser window/tab running WhatsApp Web."""
    if not (win.visible and "WhatsApp" in win.title):
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(win._hWnd)
        exe = psutil.Process(pid).name().lower()
    except Exception:
        return False
    return exe in BROWSERS

def is_whatsapp_desktop_window(win) -> bool:
    """Detect the native WhatsApp Desktop window."""
    if not (win.visible and "WhatsApp" in win.title):
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(win._hWnd)
        exe = psutil.Process(pid).name().lower()
    except Exception:
        return False
    return exe == "whatsapp.exe"

def send_via_web(chat_id: str, message: str, idx: int = 1) -> None:
    """
    Send via WhatsApp Web:
    - open or focus the chat URL
    - accept any “Click to Chat” prompt
    - paste the message from clipboard
    - press Enter to send
    """
    encoded = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={chat_id}&text={encoded}"


    # focus existing WhatsApp Web tab or open a new one
    tabs = [w for w in gw.getAllWindows() if is_whatsapp_web_window(w)]
    if tabs:
        win = tabs[0]
        win.activate()
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.typewrite(url)
        pyautogui.press("enter")
        time.sleep(30)
    else:
        webbrowser.open_new_tab(url)

    pyautogui.press("enter")
    time.sleep(1)
    # 2) paste the actual message
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)
    # 3) send it
    pyautogui.press("enter")

def send_via_desktop(chat_id: str, message: str, idx: int = 1) -> None:
    """
    Send via WhatsApp Desktop:
    - launch whatsapp:// URI
    - accept any new-chat confirmation
    - paste the message from clipboard
    - press Enter to send
    """
    uri = f"whatsapp://send?phone={chat_id}"
    try:
        os.startfile(uri)
    except Exception:
        webbrowser.open(uri)

    # wait for app + any prompt
    time.sleep(5 if idx == 1 else 2)
    # 1) accept new-chat confirmation
    pyautogui.press("enter")
    time.sleep(1)
    # 2) focus the Desktop window
    wins = [w for w in gw.getAllWindows() if is_whatsapp_desktop_window(w)]
    if wins:
        win = wins[0]
        win.activate()
        time.sleep(0.5)
    # 3) paste and send
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)
    pyautogui.press("enter")

def send_whatsapp(chat_id: str, message: str, idx: int = 1, mode: str = "auto") -> None:
    """
    Dispatch to the selected mode: "web", "desktop", or "auto".
    """
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
        raise ValueError(f"Unknown mode '{mode}'. Choose 'web', 'desktop', or 'auto'.")

def send_reminders(appointments: list, mode: str = "auto", delay: float = 2.0) -> None:
    """
    Send WhatsApp reminders for a list of appointment dicts.
    Each dict should have keys:
      - phone:            recipient phone number (string)
      - owner_name:       name of the recipient
      - pet_name:         pet’s name(s)
      - next_appointment: date string (yyyy-MM-dd)
      - reason:           appointment reason/text
    mode: "web", "desktop", or "auto"
    delay: seconds to wait between messages
    """
    for idx, v in enumerate(appointments, start=1):
        number = v.get("phone", "")
        # ensure country code
        if number.startswith("0"):
            number = "2" + number

        name   = v.get("owner_name", "")
        pet    = v.get("pet_name", "")
        date   = v.get("next_appointment", "")
        reason = v.get("reason", "")  # ← newly extracted

        ts   = int(time.time())
        link = f"https://www.facebook.com/share/1CdXFXvpQP/?_={ts}"
        message = (
            f"مرحبا {name} ,\n"
            f"عيادة Cure تذكركم بموعد الزيارة القادمة لمتابعة سلامة {pet}\n"
            f"بتاريخ {date}\n"
            f"وذلك لإجراء موعد {reason}\n\n"  # ← inserted reason line
            "و متنسوش تتابعوا نصايحنا و عروضنا على صفحة الفيسبوك:\n"
            f"{link}"
        )

        send_whatsapp(number, message, idx, mode)
        time.sleep(delay)

