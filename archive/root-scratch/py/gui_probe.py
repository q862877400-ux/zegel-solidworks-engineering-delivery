import sys
sys.stdout.reconfigure(encoding="utf-8")
for m in ("pywinauto", "uiautomation", "pyautogui", "PIL", "win32gui", "win32con", "cv2", "numpy"):
    try:
        __import__(m); print("  %-14s OK" % m)
    except ImportError:
        print("  %-14s 无" % m)