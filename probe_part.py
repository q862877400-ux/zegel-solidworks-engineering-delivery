# -*- coding: utf-8 -*-
"""验两件事：
   ① 插件生成的件是不是参数化的（配置列表 / 尺寸表 / 全局变量）
   ② 能不能插进装配
"""
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
    sp = importlib.util.spec_from_file_location(name, S / f"{name}.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m
    sp.loader.exec_module(m)
    return m


sw = load("sw_api_sldworks")
sw.get_com_member = sw_connect.get_com_member
ct = load("sw_com_traps")
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_assembly.asmdot"

BF = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
          r"Full Version v2.4.1-20260918-1\ForFaceSelector\BuildFile")
# ⚠ ~$ 开头是 SolidWorks 的锁文件（不是零件本体），必须排除
parts = [p for p in BF.iterdir()
         if p.is_file() and p.suffix.lower() == ".sldprt"
         and not p.name.startswith("~$")]
print("  BuildFile 里的件:", [p.name[:46] for p in parts])
if not parts:
    print("  没有可用文件")
    raise SystemExit(1)
part = parts[0]
print("  用这个:", part.name)

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
print("  SW", app.RevisionNumber)

asm = None
doc = None
try:
    app.CommandInProgress = True
    e, w = ct.byref_pair()
    doc = app.OpenDoc6(str(part), 1, 1, "", e, w)
    print()
    print("  ① 打开:", "成功" if doc is not None else "None")
    if doc is None:
        raise SystemExit(2)
    print("     Title :", sw.call_index(doc, "IModelDoc2", "GetTitle"))
    cfgs = sw.call_index(doc, "IModelDoc2", "GetConfigurationNames")
    print("     配置数:", len(cfgs) if cfgs else 0)
    if cfgs:
        print("     配置样例:", list(cfgs)[:10])
    # 参数化载体
    for fam, mem, label in (
        ("IModelDoc2", "GetEquationCount", "方程式数"),
        ("IModelDoc2", "GetGlobalVariableCount", "全局变量数"),
    ):
        try:
            print("     %-8s: %s" % (label, sw.call_index(doc, fam, mem)))
        except Exception as exc:
            print("     %-8s: 读不到 (%s)" % (label, str(exc)[:40]))
    try:
        dts = sw.call_index(doc, "IModelDoc2", "GetDimensionCount", 0)
        print("     尺寸数    :", dts)
    except Exception as exc:
        print("     尺寸数    : 读不到 (%s)" % str(exc)[:40])

    print()
    print("  ② 插入装配")
    asm = sw.call_index(app, "ISldWorks", "NewDocument", TPL, 2, 0.0, 0.0)
    print("     装配:", sw.call_index(asm, "IModelDoc2", "GetTitle"))

    def comps():
        return sw.call_index(asm, "IAssemblyDoc", "GetComponents", True) or ()

    print("     插前组件数:", len(comps()))
    r = sw.call_index(asm, "IAssemblyDoc", "AddComponent5",
                      str(part), 0, "", True, "", 0.0, 0.0, 0.0)
    print("     AddComponent5 ->", repr(r)[:40])
    after = comps()
    print("     插后组件数:", len(after))
    for c in after:
        print("       组件:", sw.call_index(c, "IComponent2", "Name2"))
        print("         源:", sw.call_index(c, "IComponent2", "GetPathName"))
    print()
    print("  结论:", "★ 可插入" if len(after) == 1 else "✗ 插入失败")
finally:
    if doc is not None:
        try:
            doc.CloseDoc(True)
        except Exception:
            pass
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
    except Exception:
        pass
