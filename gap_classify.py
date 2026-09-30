# -*- coding: utf-8 -*-
"""把「覆盖率缺口」按类别分清，拿到真实数字。

上一轮那个 60.48% 的口径有问题：把**枚举成员**也算成了「能力成员」。
本脚本把官方反射的成员按四类分开：
    A 能力成员   —— 接口上的方法 / 属性（**这才是真缺口**）
    B 枚举成员   —— 枚举类型的成员（**不算缺口**）
    C 排除域     —— sustainability / sw3dprinter / swbrowser（**你明说排除**）
    D 内部口     —— IGetXxx / IUpdateYyy 形式（**刻意不索引**）
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAW = Path(r"D:\AI\SW\_raw")
SCRIPTS = Path(r"C:\swprojects\sw-skill-fork\scripts")
EXCLUDE = ("sustainability", "sw3dprinter", "swbrowser", "swtbt")


def parse(path: Path):
    """反射转储：返回 (方法名集合, 属性名集合, 枚举名集合)。"""
    meth, prop, enu = set(), set(), set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        m = re.match(r"^(\S+)\s+(\w+)\s*\(", s)
        if m:
            name = m.group(2)
            (prop if name.startswith(("get_", "set_")) else meth).add(
                re.sub(r"^(get|set)_", "", name))
            continue
        # 枚举行形如 "swEndConditions_e.swEndCondMidPlane = 2"
        m = re.match(r"^(\w*_e)\.(\w+)\s*=", s)
        if m:
            enu.add((m.group(1), m.group(2)))
    return meth, prop, enu


def main() -> int:
    mine: set[str] = set()
    for p in SCRIPTS.glob("sw_api_*.py"):
        c = p.read_text(encoding="utf-8")
        mine |= set(re.findall(r"^        '(\w+)': \d+,", c, re.M))
        mine |= set(re.findall(r"^        '(\w+)',", c, re.M))

    rows = []
    for rf in sorted(RAW.rglob("iface_*.txt")):
        asm = re.search(r"iface_(.+)\.txt$", rf.name).group(1).lower()
        meth, prop, enu = parse(rf)
        cap = meth | prop
        enu_names = {n for _, n in enu}
        if asm in EXCLUDE:
            rows.append((asm, len(cap), 0, len(cap) - 0, "C 排除域"))
            continue
        # 排除 COM 内部分发口：IGetXxx / IUpdateYyy / IAddMate 这类
        #   —— 它们是**同一能力的内部变体**，COM 名与正式成员重复
        #   （例 IAddMate 就是 AddMate 的内部分发口），
        #   正式成员在 mine 里已有 ⇒ 不算能力缺口。
        internal = {n for n in cap if n[1:2].isupper() and n not in mine}
        cap = cap - internal
        miss_cap = cap - mine
        miss = miss_cap - enu_names
        rows.append((asm, len(cap), len(cap) - len(miss), len(miss), ""))

    rows.sort(key=lambda r: -r[3])
    print("  %-24s %10s %8s %8s  %s" % ("程序集", "官方能力", "已登记", "缺口", "备注"))
    print("  " + "-" * 66)
    tot_o = tot_m = 0
    for asm, o, m, miss, note in rows:
        tot_o += o
        tot_m += m
        print("  %-24s %10d %8d %8d  %s" % (asm, o, m, miss, note))
    print("  " + "-" * 66)
    print("  %-24s %10d %8d %8d" % ("合计", tot_o, tot_m, tot_o - tot_m))
    print()
    print("  ★ 排除 3 个域后的真实覆盖率：%.2f%%"
          % (100.0 * tot_m / max(tot_o, 1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
