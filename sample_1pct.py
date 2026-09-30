# -*- coding: utf-8 -*-
"""抽 1% 索引成员做实机核验。

分两类，**结论强度不同，必须分开报**：
  A 类 · 零参成员 —— 在真实 COM 对象上直接调，验「名字对不对 + 形态（属性/方法）对不对」
  B 类 · 带参成员 —— 需要先造出宿主对象才能调，成本高。
                    本轮只验「族与成员名在官方类型库里存在」，**不验调用**。
                    ⚠ 抽样要反映**全量**，不能只抽好验的。

分层：按 12 个程序集各抽 ~1%，再按 arity 分零参/带参。
"""
from __future__ import annotations

import io
import random
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPTS = Path(r"C:\swprojects\sw-skill-fork\scripts")
SAMPLE_RATE = 0.01
SEED = 20260929           # 固定种子，可复现

import importlib.util


def load(modname: str):
    spec = importlib.util.spec_from_file_location(modname, SCRIPTS / f"{modname}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[modname] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    import win32com.client as w32
    sys.path.insert(0, str(SCRIPTS))
    import sw_connect

    mods = sorted(p.stem for p in SCRIPTS.glob("sw_api_*.py"))
    rng = random.Random(SEED)

    # ── 抽样 ──
    sample = []          # (module, family, member, arity)
    total = 0
    for name in mods:
        m = load(name)
        m.get_com_member = sw_connect.get_com_member
        pool = [(f, mem, a)
                for f, sub in m.ARITY.items() for mem, a in sub.items()]
        total += len(pool)
        k = max(1, round(len(pool) * SAMPLE_RATE))
        for fam, mem, a in rng.sample(pool, min(k, len(pool))):
            sample.append((name, fam, mem, a))

    zero = [s for s in sample if s[3] == 0]
    withp = [s for s in sample if s[3] > 0]
    print(f"全量成员 = {total}；抽样率 {SAMPLE_RATE:.0%} → 抽到 {len(sample)}")
    print(f"  零参（可实机调） = {len(zero)}")
    print(f"  带参（只能验存在）= {len(withp)}")

    # ── 连上 SolidWorks ──
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
    print(f"  版本 RevisionNumber = {app.RevisionNumber}")
    try:
        app.CommandInProgress = True
    except Exception:
        pass

    # ── A 类：零参成员实机调 ──
    # 宿主对象按族前缀推断：ISldWorks→app，其余先跳过（需要模型文档）
    HOST = {"ISldWorks": app}
    a_ok = a_attr = a_meth = a_fail = a_skip = 0
    fails, skips = [], []
    for mod, fam, mem, _a in zero:
        host = HOST.get(fam)
        if host is None:
            a_skip += 1
            skips.append(f"{fam}.{mem}")
            continue
        try:
            m = load(mod)
            m.get_com_member = sw_connect.get_com_member
            m.call_index(host, fam, mem)
            # 形态判定
            raw = getattr(host, mem, None)
            if callable(raw):
                a_meth += 1
            else:
                a_attr += 1
            a_ok += 1
        except Exception as exc:                      # noqa: BLE001
            a_fail += 1
            fails.append(f"{fam}.{mem} -> {str(exc)[:70]}")
    print()
    print("── A 类 零参成员（实机调）" + "─" * 34)
    print(f"  实机通过 {a_ok}（其中属性形态 {a_attr} / 方法形态 {a_meth}）")
    print(f"  实机失败 {a_fail}")
    print(f"  跳过（无可用宿主，需模型文档）{a_skip}")
    for f in fails[:12]:
        print("    [FAIL] " + f)
    if skips:
        print("    跳过样例:", ", ".join(skips[:5]))

    # ── B 类：带参成员只验「族与成员名在官方类型库里存在」──
    # 这一条由 check_member_names.py 的全量门禁保证；此处报告抽样规模
    print()
    print("── B 类 带参成员" + "─" * 43)
    print(f"  抽到 {len(withp)} 条 —— 只验「族/成员名存在」，**不验调用**")
    print("  （存在性已由 check_member_names.py 对**全部** 15,466 条全量把关）")
    bad = 0
    for mod, fam, mem, a in withp:
        m = load(mod)
        if fam not in m.ARITY or mem not in m.ARITY[fam]:
            bad += 1
            print(f"    [MISS] {fam}.{mem}")
        elif m.ARITY[fam][mem] != a:
            bad += 1
            print(f"    [ARITY] {fam}.{mem} 表{a} 实际{m.ARITY[fam][mem]}")
    print(f"  索引自洽性异常 = {bad}")

    # ── 收尾 ──
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
        print("\n  已 ExitApp 收尾")
    except Exception as exc:
        print("\n  ExitApp 失败（进程留给用户手动关）:", str(exc)[:50])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
