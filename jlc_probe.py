# -*- coding: utf-8 -*-
"""验证：JLCFA 模型包是不是「一个参数化模板 + 全部规格作为配置」。"""
import sys
import time
import zipfile
import importlib.util
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
         r"Full Version v2.4.1-20260918-1\ForFaceSelector\model")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, str(S))
import sw_connect
import win32com.client as w32

sp = importlib.util.spec_from_file_location("swapi", S / "sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp)
sys.modules["swapi"] = sw
sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member

# 挑一个内部文件名带 ~N 的（说明有配置）
target = None
for z in sorted(B.glob("*.zip")):
    with zipfile.ZipFile(z) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        if names and "~" in names[0]:
            target = (z, names[0])
            break
if not target:
    for z in sorted(B.glob("*.zip"))[:20]:
        with zipfile.ZipFile(z) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if names:
                target = (z, names[0])
                break

z, inner = target
print("  包:", z.name)
print("  内部:", inner)

tmp = Path(tempfile.gettempdir()) / ("jlcfa_probe_" + z.stem)
tmp.mkdir(exist_ok=True)
with zipfile.ZipFile(z) as zf:
    zf.extractall(tmp)
model = tmp / inner
print("  解出:", model.name, "%.1f MB" % (model.stat().st_size / 1e6))

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
e, w = __import__("sw_com_traps", fromlist=["x"]).byref_pair() \
    if False else (None, None)
sys.path.insert(0, str(S))
import importlib as _il
ct = _il.import_module("sw_com_traps") if "sw_com_traps" in sys.modules else None
if ct is None:
    s2 = _il.util.spec_from_file_location("sw_com_traps", S / "sw_com_traps.py")
    ct = _il.util.module_from_spec(s2)
    sys.modules["sw_com_traps"] = ct
    s2.loader.exec_module(ct)
e, w = ct.byref_pair()
try:
    app.CommandInProgress = True
    print()
    print("  ★ 打开这个参数化模板，读它的配置表：")
    d = app.OpenDoc6(str(model), 1, 1, "", e, w)
    print("    OpenDoc6 ->", "成功" if d is not None else "None")
    if d is not None:
        title = sw.call_index(d, "IModelDoc2", "GetTitle")
        cfgs = sw.call_index(d, "IModelDoc2", "GetConfigurationNames")
        print("    Title    :", title)
        print("    配置总数 :", len(cfgs) if cfgs else 0)
        if cfgs:
            print("    配置样例:", list(cfgs)[:12])
        drw = sw.call_index(d, "IModelDoc2", "GetActiveConfiguration")
        print("    当前配置 :", sw.call_index(drw, "IConfiguration", "Name"))
finally:
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
    except Exception:
        pass
