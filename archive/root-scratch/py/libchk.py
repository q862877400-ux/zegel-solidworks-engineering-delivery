import sys
sys.stdout.reconfigure(encoding="utf-8")
for m in ("pywinauto","uiautomation","pyautogui","pygetwindow","win32gui","win32api",
          "comtypes","PIL","cv2","numpy","mouse","keyboard","pynput"):
    try:
        mod=__import__(m); print("  %-14s OK %s" % (m, getattr(mod,"__version__","")))
    except ImportError: print("  %-14s 无" % m)