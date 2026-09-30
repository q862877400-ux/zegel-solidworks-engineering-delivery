import sys
sys.stdout.reconfigure(encoding="utf-8")
for m in ("pywinauto", "uiautomation"):
    try:
        mod = __import__(m); print("  %-14s OK  %s" % (m, getattr(mod, "__version__", "")))
    except ImportError as e:
        print("  %-14s 失败 %s" % (m, str(e)[:50]))