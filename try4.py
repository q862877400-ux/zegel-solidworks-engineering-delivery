# -*- coding: utf-8 -*-
import sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts"); sys.path.insert(0, str(S))
import sw_connect, win32com.client as w32
sp = importlib.util.spec_from_file_location("swapi", S/"sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw; sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
P = r"D:\SOLIDWORKS Data\browser\GB\washers and rings\lock washers\lock washers external teeth gb.sldprt"
app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try: _ = app.RevisionNumber; break
    except Exception: time.sleep(1)
asm = None
try:
    app.CommandInProgress = True
    asm = sw.call_index(app, "ISldWorks", "NewDocument", TPL, 2, 0.0, 0.0)
    print("  装配:", sw.call_index(asm, "IModelDoc2", "GetTitle"))
    def count(): return len(sw.call_index(asm, "IAssemblyDoc", "GetComponents", True) or ())
    print("  初始组件数:", count())
    trials = [
        ("AddComponent5(path,0,'',True,'',0,0,0)", "IAssemblyDoc","AddComponent5", (P,0,"",True,"",0.0,0.0,0.0)),
        ("AddComponent5(path,0,'',False,'',0,0,0)", "IAssemblyDoc","AddComponent5", (P,0,"",False,"",0.0,0.0,0.0)),
        ("AddComponent4(path,'',0,0,0)",           "IAssemblyDoc","AddComponent4", (P,"",0.0,0.0,0.0)),
        ("AddComponent2(path,0,0,0)",             "IAssemblyDoc","AddComponent2", (P,0.0,0.0,0.0)),
    ]
    for label, fam, mem, args in trials:
        try:
            r = sw.call_index(asm, fam, mem, *args)
            c = count()
            print("  %-38s -> %-22s 组件数=%d" % (label, repr(r)[:22], c))
            if c > 0: print("     ★ 成功！"); break
        except Exception as e:
            print("  %-38s ERR %s" % (label, str(e)[:52]))
    print()
    print("  零件文件配置数（先单独打开看）:")
    try:
        pdoc = sw.call_index(app, "ISldWorks", "OpenDoc6", P, 1, 1, "", None, None)
        print("    OpenDoc6 ->", repr(pdoc))
        if pdoc is not None:
            print("    配置名:", sw.call_index(pdoc, "IModelDoc2", "GetConfigurationNames"))
    except Exception as e:
        print("    ERR", str(e)[:70])
finally:
    if asm is not None:
        try: asm.CloseDoc(True)
        except Exception: pass
    try: app.CommandInProgress = False
    except Exception: pass
    try: app.ExitApp()
    except Exception: pass