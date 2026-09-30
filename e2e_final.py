# -*- coding: utf-8 -*-
"""最终端到端：Toolbox 索引 → 查零件 → 建装配 → 插入 → 回读 → 收尾。"""
import sys
import time
import importlib.util
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, str(S))
import sw_connect
import win32com.client as w32


def load(name):
    spec = importlib.util.spec_from_file_location(name, S / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


ct = load("sw_com_traps")
tbi = load("sw_toolbox_index")
sw = load("sw_api_sldworks")
sw.get_com_member = sw_connect.get_com_member

TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
part = tbi.search("lock washers external teeth", standard="GB")[0]
print("  ① 索引查到零件:", part["part"])
print("     路径        :", part["path"])

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
print("  ② SolidWorks  :", app.RevisionNumber)

asm = None
try:
    app.CommandInProgress = True
    asm = sw.call_index(app, "ISldWorks", "NewDocument", TPL, 2, 0.0, 0.0)
    print("  ③ 建装配      :", sw.call_index(asm, "IModelDoc2", "GetTitle"))

    def comps():
        return sw.call_index(asm, "IAssemblyDoc", "GetComponents", True) or ()

    print("  ④ 插前组件数  :", len(comps()))
    r = sw.call_index(asm, "IAssemblyDoc", "AddComponent5",
                       part["path"], 0, "", True, "", 0.0, 0.0, 0.0)
    print("     AddComponent5 ->", repr(r)[:40])
    after = comps()
    print("  ⑤ 插后组件数  :", len(after))
    for c in after:
        print("     组件:", sw.call_index(c, "IComponent2", "Name2"))
        print("       源:", sw.call_index(c, "IComponent2", "GetPathName"))
    print()
    print("  结论:", "端到端成功" if len(after) == 1 else "仍未插入")
finally:
    if asm is not None:
        try:
            asm.CloseDoc(True)
        except Exception:
            pass
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
        print("  收尾: CommandInProgress=False + ExitApp（无残留进程）")
    except Exception:
        pass
