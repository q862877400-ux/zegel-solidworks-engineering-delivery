from pathlib import Path
p = Path(r"D:\AI\SW\locate_sw.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    try:
        import psutil
        name = psutil.Process(win32process.GetWindowThreadProcessId(h)[1]).name()
    except Exception:
        name = ""
    if name.lower() == "sldworks.exe":''',
'''    # ⚠ 不用 psutil（本机没有）：直接问内核要这个窗口所属进程的可执行路径
    import win32api
    import win32con
    name = ""
    try:
        pid = win32process.GetWindowThreadProcessId(h)[1]
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        name = win32process.GetModuleFileNameEx(hproc, 0) or ""
        hproc.Close()
    except Exception:
        # 拿不到路径时退回进程名（同样够用）
        try:
            import subprocess
            pid = win32process.GetWindowThreadProcessId(h)[1]
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
    if name.lower().endswith("sldworks.exe"):''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  改用 win32api 取进程路径，不引新依赖")