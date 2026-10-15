# -*- coding: utf-8 -*-
"""端到端（正确路径）：Toolbox 索引 -> 建装配 -> 插零件 -> 回读 -> 收尾。

⚠ 本次教训：前两次我**绕过 get_com_member 直接加括号**，
   于是把「属性形态成员」误报成 bug。get_com_member 本身是对的。
   ⇒ 本脚本**一律经 call_index**，不裸写 obj.Member()。
"""
import sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts"); sys.path.insert(0, str(S))
import sw_connect, win32com.client as w32
tbi = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("tbi", S/"sw_toolbox_index.py"))
sys.modules["tbi"]=tbi
importlib.util.spec_from_file_location("tbi", S/"sw_toolbox_index.py").loader.exec_module(tbi)
sp = importlib.util.spec_from_file_location("swapi", S/"sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw; sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
part = tbi.search("lock washers external teeth", standard="GB")[0]
print("  零件:", part["part"])
app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try: _ = app.RevisionNumber; break
    except Exception: time.sleep(1)
print("  SW", app.RevisionNumber)
asm = None
try:
    app.CommandInProgress = True
    asm = sw.call_index(app, "ISldWorks", "NewDocument", TPL, 2, 0.0, 0.0)
    print("  装配已建:", sw.call_index(asm, "IModelDoc2", "GetTitle"))
    before = sw.call_index(asm, "IAssemblyDoc", "GetComponents", True) or ()
    print("  插前组件数:", len(before))
    # ⚑ GetComponents2 **不存在** —— 官方真名是 GetComponents(1 参)。
    #   又一次「凭印象写 API」，被护栏当场拦下。
    ok = sw.call_index(asm, "IAssemblyDoc", "AddComponent5",
                       part["path"], 0, "", True, "", 0.0, 0.0, 0.0)
    print("  AddComponent5 ->", ok)
    after = sw.call_index(asm, "IAssemblyDoc", "GetComponents", True) or ()
    print("  插后组件数:", len(after))
    for c in after:
        n = sw.call_index(c, "IComponent2", "Name2")
        p = sw.call_index(c, "IComponent2", "GetPathName")
        print("    组件:", n)
        print("      源:", p)
    print()
    print("  结果:", "端到端成功" if len(after) == len(before) + 1 else "未插入")
finally:
    if asm is not None:
        try: asm.CloseDoc(True)
        except Exception: pass
    try: app.CommandInProgress = False
    except Exception: pass
    try: app.ExitApp()
    except Exception: pass