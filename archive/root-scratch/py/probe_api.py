# -*- coding: utf-8 -*-
"""①③ 纯读取：不打开任何零件文件，只问 SolidWorks 要加载项对象和命令列表。

⚠ 安全约束（上次崩掉的教训）
  · **绝不调用 OpenDoc6 / NewDocument / AddComponent** —— 崩在那一步
  · 只调 GetAddInObject / GetCommandIds 这类纯查询
  · CommandInProgress 拦弹窗，try/finally 收尾，ExitApp 退出
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

sp = importlib.util.spec_from_file_location("swapi", S / "sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp)
sys.modules["swapi"] = sw
sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member

ADDIN_KEY = "{0cfa12b7-7c14-41d4-9fdf-572817bcc990}"


def main() -> int:
    app = w32.dynamic.Dispatch("SldWorks.Application")
    for _ in range(40):
        try:
            _ = app.RevisionNumber
            break
        except Exception:
            time.sleep(1)
    print("  SW", app.RevisionNumber)
    try:
        app.CommandInProgress = True
        print()
        print("  ③ SolidWorks 命令表里有没有它注册的：")
        try:
            cm = sw.call_index(app, "ISldWorks", "GetCommandManager", 1)   # 1=模型
            print("     命令管理器:", repr(cm)[:40])
        except Exception as e:
            print("     ERR", str(e)[:60])
        print()
        print("  ① 加载项对象（GetAddInObject）：")
        for progid in ("sw_fa_prod_selector", "ForfaceSwDriverCoreOffline",
                       "sw-fa-prod-selector35", "JLCFA", "ForFaceSelector"):
            try:
                o = sw.call_index(app, "ISldWorks", "GetAddInObject", progid)
                print("     %-30s -> %s" % (progid, repr(o)[:40]))
                if o is not None:
                    dump_members(o, progid)
            except Exception as e:
                print("     %-30s ERR %s" % (progid, str(e)[:44]))
        return 0
    finally:
        try:
            app.CommandInProgress = False
        except Exception:
            pass
        try:
            app.ExitApp()
            print("\n  收尾: ExitApp（无残留进程）")
        except Exception:
            pass


def dump_members(obj, tag: str) -> None:
    """列出对象上非 IDispatch 通用方法的成员 —— 找插件自定义接口。"""
    skip = {"QueryInterface", "AddRef", "Release", "GetTypeInfo",
            "GetIDsOfNames", "Invoke", "GetTypeInfoCount"}
    names = []
    for cand in dir(obj):
        if cand in skip or cand.startswith("_"):
            continue
        if not (cand[:1].isupper()):
            continue
        names.append(cand)
    print("        成员 %d 个:" % len(names))
    for n in sorted(names)[:40]:
        print("          %s" % n)


if __name__ == "__main__":
    raise SystemExit(main())
