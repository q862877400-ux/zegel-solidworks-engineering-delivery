import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
try:
    from scripts.sw_connect import connect_solidworks
    sw,_m,_x = connect_solidworks(wait_seconds=10, return_metadata=True)
    print("  已连上，调 ExitApp()")
    sw.ExitApp()
except Exception as e:
    print("  ExitApp 失败（改用 Stop-Process）: %s" % str(e)[:80])