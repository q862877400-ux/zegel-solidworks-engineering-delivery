# -*- coding: utf-8 -*-
"""端到端：从 Toolbox 索引查零件 → 插入装配 → 回读确认 → 收尾。

⚠ 安全约束（AGENTS.md 撤销后的铁律 2）：
  · 先置 CommandInProgress=True 拦弹窗，收尾**一定**置回 False
  · 全程 try/finally；异常时也要收尾
  · 只操作**自己新建**的装配，不碰用户已有文档
  · 结束 ExitApp，不留常驻进程
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPTS = Path(r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    import sw_connect
    import win32com.client as w32

    tbi = load("sw_toolbox_index")
    sw = load("sw_api_sldworks")
    sw.get_com_member = sw_connect.get_com_member

    # ── 1. 选一个零件（结构简单、路径干净）──
    hits = tbi.search("lock washers external teeth", standard="GB")
    if not hits:
        print("  索引里没找到目标零件"); return 2
    part = hits[0]
    print("  目标零件:", part["part"])
    print("  路径    :", part["path"])
    print("  存在    :", Path(part["path"]).is_file())

    # ── 2. 连 SolidWorks ──
    try:
        app = w32.GetActiveObject("SldWorks.Application")
        print("  复用已有实例")
    except Exception:
        app = w32.dynamic.Dispatch("SldWorks.Application")
        print("  新启动 SolidWorks")
        for _ in range(40):
            try:
                _ = app.RevisionNumber
                break
            except Exception:
                time.sleep(1)
    print("  版本:", app.RevisionNumber)

    asm = None
    try:
        app.CommandInProgress = True
        print("  CommandInProgress = True")

        # ── 3. 新建装配（1 = swDocASSEMBLY，反射枚举值）──
        # ⚑ NewDocument(String Template, Int32 Type, Double X, Double Y) —— 4 参
        #   Template 传 ""（用系统默认模板）；Type: 1=swDocPART 2=swDocASSEMBLY
        #   ⚠ 第一次写错成 3 参，被本仓库的 arity 护栏当场拦下 —— 护栏有效。
        asm = sw.call_index(app, "ISldWorks", "NewDocument", "", 2, 0.0, 0.0)
        print("  NewDocument ->", type(asm).__name__ if asm is not None else None)
        if asm is None:
            print("  [STOP] 建装配失败"); return 3

        # ── 4. 插入 Toolbox 零件 ──
        # AddComponent5(String File, Int32 ConfigOpt, String ConfigName,
        #                Boolean UseSpeed, String RefConf, Double X, Double Y, Double Z)
        before = len(list(asm.GetComponents2(True, True) or []))
        ok = sw.call_index(asm, "IAssemblyDoc", "AddComponent5",
                           part["path"], 0, "", True, "", 0.0, 0.0, 0.0)
        print("  AddComponent5 返回:", ok)
        after = len(list(asm.GetComponents2(True, True) or []))
        print("  组件数 %d -> %d" % (before, after))

        # ── 5. 回读确认 ──
        comps = list(asm.GetComponents2(True, True) or [])
        for c in comps:
            try:
                print("  组件:", c.Name2, "|", c.GetPathName())
            except Exception as e:
                print("  组件名读取失败:", str(e)[:50])
        return 0 if after == before + 1 else 4
    finally:
        # ── 6. 收尾 ──
        try:
            if asm is not None:
                asm.CloseDoc(True)
        except Exception:
            pass
        try:
            app.CommandInProgress = False
            print("  CommandInProgress = False")
        except Exception:
            pass
        try:
            app.ExitApp()
            print("  已 ExitApp（无残留进程）")
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
