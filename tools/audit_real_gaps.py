r"""@brief **真缺口审计（⚠ 提示性，不是判据）**：能力层公开函数里，**可能**还没有入口的那些。

⚠⚠⚠ **在做任何「审计 / 覆盖 / 缺口 / 映射」类工具之前，先读 `docs/history/module-capability-coverage.md`**
```
★ 那份文档（轮 118 / Spec Kit `037`）的**第一行结论**就是：
  > 「**结论：这个核对不能做成门禁，而且它问的问题本身是错的。**」
★★ 而轮 256-257 我**在没读到它**的情况下又造了一遍（★ 见 known-facts 190）——
  ★ 它试过**三版判据**（模块名 / 函数名 / 并集），假阳性 43 / 43 / 38，
  ★ 并定性为「本项目**第 8 次**按名字做的检查产出大量假阳性」。
★★★ 它的**根因**：★ **A1 的单位是「域（domain）」，不是「文件（module）」**
  ⇒ `capabilities.yaml` 的条目**本来就是域级的** ⇒ ★ **"模块名没出现"根本不是缺陷**。
⇒ ★★★★ **所以"哪些函数没有工具"与"哪些文件没有条目"是**同一个错问题****。
  ★ **正解：逐域人工判断**（★ 原话：「那是**判断**，不是匹配」）。
★ **先 `ls docs/` + grep `gap` / `coverage` / `missing` / `entry`** —— ★ 一次就够。
```

## ⚠⚠⚠ **本脚本的输出**不是**真缺口**（2026-10-01 轮 256 实测自证）
```
★ 它按**名字**匹配 ⇒ **必然假报**。实测（轮 256 一跑就露）：
    · 它把 `shell` / `rib` / `insert_dome` 报成"真缺口" —— ★★ **而它们**刚挂过****
      （工具入口是 `shell_report` / `rib_report` / `insert_dome_report`，★ **名字不同**）
    · 它把 `add_pressure` 报成缺口 —— ★ **而 `apply_pressure_report` 就是它的入口**
    · 它把 `get_topology_study_manager` 报成缺口 —— ★ **而 `topology_manager_report` 是入口**
    · 它把 `sw_surface` 的 16 个报成缺口 —— ★ **而曲面族"明确不做"**（known-facts 40）
    · 它把 `resolve_selection` 报成缺口 —— ★ **而那是内部辅助**，不是工具候选
⇒ ★★★ **所以本脚本只能当"**提示器**"**（★ 提示"这批函数值得看一眼"），
   ★★ **不能当"缺口判据"**（★ 拿它当判据就会去做**重复的**活）。
```

## ★★★ 那正解是什么（★ 本轮的结论）
```
★★★ **"真缺口"做不到自动算** —— 因为工具名与能力层函数名之间**没有可推导的映射**
  （`X` / `X_report` / `X_evidence` / `apply_X` / `list_X` 都可能）。
⇒ ★★★★ **正解 = 维护一张**显式映射表****（★ 照本项目 `check_interface_member_ownership` 的
  `MANUAL_MAP` 先例：★ **"没有依据的不许进来"**、★ **每条注明依据**）。
⇒ ★★★★★ **而在此之前，本脚本的用法是**：★ **跑一遍、人工逐条判** ——
  ★ 判"这条是不是已被某个工具覆盖"（★ 覆盖了就在表里记一行、下次不再问）。
```

## ★★ 它仍然有用（★ 别丢掉）
```
★ 轮 256 靠它**当场发现**："`sw_hole_features` 未挂 13"是**虚高** ——
  实测 **5 个已被 `mcp-server/server.py`（上游现成 45 个工具）覆盖**
  ⇒ ★★ **那个"13"是**按函数名**算出来的，而功能**早就有入口****。
★ 所以它的价值是：★ **把"我们有什么"摆到一屏上**（公开 / 有工具 / 上游调 / 疑似缺口）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（审计工具）
# 文件:   tools/audit_real_gaps.py
# 定位:   ⚠ **提示性**审计（★ **不是判据** —— 见上面的自证）；把三层口径摆到一屏。
# 官方依据: 不适用（本项目内部口径）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

#: ★ 受检模块（★ 需要时往这里加）
MODULES = (
    "sw_part",
    "sw_simulation",
    "sw_simulation_loads",
    "sw_topology",
    "sw_hole_features",
    "sw_weldment",
    "sw_document_data",
    "sw_export",
    "sw_selection_spec",
    "sw_surface",
)


def main() -> int:
    import register_capabilities as rc

    ours: dict[str, set] = {}
    for spec in rc.all_specs():
        ours.setdefault(spec.module, set()).add(spec.function)

    server = ROOT / "mcp-server" / "server.py"
    srv_text = (
        server.read_text(encoding="utf-8", errors="replace") if server.is_file() else ""
    )
    #: ★ 第 ② 层：server.py 里**被调用的**能力层函数名
    srv_called = set(re.findall(r"\b([a-z_][a-z0-9_]{2,})\s*\(", srv_text))

    #: ★ 第 ③ 层：能力层内部的**上层包装**（谁在别处被调用）
    all_text = "\n".join(
        f.read_text(encoding="utf-8", errors="replace")
        for f in list((ROOT / "scripts").glob("*.py"))
        + list((ROOT / "mcp-server").glob("*.py"))
        + list((ROOT / "tools").glob("*.py"))
    )

    print("真缺口审计 · 三层口径（① 我们的工具 ② 上游 server.py ③ 上层包装只提示）")
    print(
        "  %-22s %5s %6s %7s %8s  %s"
        % ("模块", "公开", "有工具", "上游调", "真缺口", "被上层包装的（提示）")
    )
    tot = {"pub": 0, "ours": 0, "srv": 0, "real": 0}
    detail: dict[str, list] = {}
    for m in MODULES:
        try:
            mod = __import__("scripts.%s" % m, fromlist=["x"])
        except Exception as exc:  # noqa: BLE001
            print("  %-22s ⚠ 导不进: %s" % (m, str(exc)[:44]))
            continue
        pub = [
            n
            for n in dir(mod)
            if not n.startswith("_")
            and callable(getattr(mod, n))
            and getattr(getattr(mod, n), "__module__", "").endswith(m)
        ]
        have = ours.get(m, set())
        by_srv = {n for n in pub if n in srv_called}
        real = [n for n in pub if n not in have and n not in by_srv]
        #: ★ 第 ③ 层：真缺口里，有多少**在别处被调用**（⇒ 多半已被上层包装）
        wrapped = [
            n
            for n in real
            if len(re.findall(r"\b%s\s*\(" % re.escape(n), all_text)) > 1
        ]
        tot["pub"] += len(pub)
        tot["ours"] += len(have & set(pub))
        tot["srv"] += len(by_srv)
        tot["real"] += len(real)
        detail[m] = real
        print(
            "  %-22s %5d %6d %7d %8d  %s"
            % (
                m,
                len(pub),
                len(have & set(pub)),
                len(by_srv),
                len(real),
                (", ".join(wrapped[:4]) + ("…" if len(wrapped) > 4 else ""))
                if wrapped
                else "—",
            )
        )
    print()
    print(
        "  合计：公开 %d · 有我们工具 %d · 被上游调 %d ⇒ ★ **真缺口 %d**"
        % (tot["pub"], tot["ours"], tot["srv"], tot["real"])
    )
    print()
    print("  ★ 真缺口逐条（★ 挂不挂要看规则 3 / 是否需要新注入键 —— 本脚本不判那个）：")
    for m, names in detail.items():
        if names:
            print("    %-22s %s" % (m, ", ".join(names)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
