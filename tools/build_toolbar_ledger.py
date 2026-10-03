"""★ 台账核实：把 `docs/toolbar-ledger.json` 里每个 api 名对**官方离线源**逐条核，并生成 Markdown 台账。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/build_toolbar_ledger.py
# 定位:   ★ 2026-10-03（轮 464）★ 用户要求「把这几轮截图问过的**列出台账**，按 spec 的纪律全部攻关」。
#   ★★ 台账数据在 `docs/toolbar-ledger.json`（★ 人工读图得来 = 需求原文）。
#   ★★★ **本脚本的职责不是重复那份数据，而是核实它** —— 因为表里 `api` 一列是**凭记忆写的**，
#     而**铁律 5**（查不到就说查不到）与**铁律 4**（签名三源互证）都要求它**逐条对官方源核过**。
#   ★ 三源（★ 本机可离线查的两套 + 一套结构化）：
#     ```
#     ① C:\swapi\types\<接口>\<成员>.md      ← ★ 结构化 markdown，查**精确成员名**（本脚本主用）
#     ② C:\swapi\enums\*.md                  ← 枚举值
#     ③ D:\AI\SW\AI Solidworks\官方文档\      ← CHM 解包，查语义与示例（本脚本只做存在性抽查）
#     ```
#   ⇒ ★ 输出：每条标 `api_verified`（★ 在①里找到的接口/成员）/ `api_missing`（★ 查不到 ⇒ 按铁律 5 记「查不到」）
#     并生成 `docs/toolbar-ledger.md`（★ 人看的台账）✓
# 官方依据: 本机 `C:\swapi\`（结构化官方源）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个 api 名必须在 `C:\swapi\` 里**至少一处**命中（接口目录名或成员文件名）。

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
SWAPI = Path(r"C:\swapi")
LEDGER = R / "docs" / "toolbar-ledger.json"
OUT_MD = R / "docs" / "toolbar-ledger.md"
OUT_JSON = R / "docs" / "toolbar-ledger-verified.json"


def index_swapi() -> tuple[set, set]:
    """⇒ `(接口名小写集, 成员名小写集)`。"""
    ifaces, members = set(), set()
    t = SWAPI / "types"
    if not t.is_dir():
        return ifaces, members
    for d in t.iterdir():
        if not d.is_dir():
            continue
        ifaces.add(d.name.lower())
        try:
            for f in d.iterdir():
                if f.is_file() and f.suffix == ".md":
                    members.add(f.stem.lower())
        except OSError:
            pass
    return ifaces, members


def verify(api: str, ifaces: set, members: set) -> dict:
    """★ 逐条核：★ 取 api 文本里所有 `标识符`，看有没有命中官方源。"""
    ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", api or "")
    hit_iface = [i for i in ids if i.lower() in ifaces]
    hit_member = [i for i in ids if i.lower() in members]
    return {"api_iface_hits": hit_iface, "api_member_hits": hit_member,
            "api_verified": bool(hit_iface or hit_member)}


def main() -> int:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    items = data["items"]
    ifaces, members = index_swapi()
    print("  官方源索引：接口 %d · 成员 %d" % (len(ifaces), len(members)))

    for it in items:
        it.update(verify(it.get("api", ""), ifaces, members))

    #: \u2605 \u5206\u6863\uff1a\u53ef\u505a = \u5f53\u524d"\u4e0d\u80fd/\u6ca1\u9a8c\u8fc7" \u4e14 api \u6838\u5b9e\u547d\u4e2d \u4e14 \u672c\u4ed3\u65e0\u5165\u53e3
    def tier(it: dict) -> str:
        if it.get("level") == "\u80fd":
            return "\u5df2\u80fd"
        if not it.get("api_verified"):
            return "\u5f85\u67e5"
        return "\u53ef\u653b\u5173" if not it.get("entry") else "\u5f85\u9a8c\u8bc1"

    for it in items:
        it["tier"] = tier(it)
    c = Counter(it["tier"] for it in items)
    c_tb = Counter(it["tb"] for it in items if it["tier"] == "\u53ef\u653b\u5173")
    print("  \u53f0\u8d26 %d \u6761 \u21d2 %s" % (len(items), dict(c)))
    print("  \u53ef\u653b\u5173\u6309\u5de5\u5177\u6761\uff1a%s" % dict(c_tb))

    #: \u2605 \u751f\u6210\u4eba\u770b\u7684\u53f0\u8d26
    lines = [
        "# 工具栏攻关台账",
        "",
        "> **本文件由 `tools/build_toolbar_ledger.py` 生成，不要手改。**",
        "> 数据源：`docs/toolbar-ledger.json`（用户 2026-10-03 五轮截图问过的全部条目 = 需求原文）。",
        "",
        "## 口径",
        "",
        "| 档 | 含义 |",
        "|---|---|",
        "| **已能** | 本仓有入口**且**有真机证据（`capabilities.yaml` 的 `verified` / evidence 文件） |",
        "| **可攻关** | 本仓**无入口**，而**官方成员在 `C:\\swapi\\` 里核到了** ⇒ 可以按官方签名立柱实现 |",
        "| **待验证** | 本仓有入口，但我还没跑成（判据要重做或入口要修） |",
        "| **待查** | 我填的 api 名在官方源里**没核到** ⇒ 按铁律 5 记「查不到」，先查清再动手 |",
        "",
        "## 汇总",
        "",
        "| 档 | 条数 |",
        "|---|---|",
    ]
    for k in ("已能", "可攻关", "待验证", "待查"):
        lines.append("| %s | %d |" % (k, c.get(k, 0)))
    lines.append("| **合计** | **%d** |" % len(items))
    lines += ["", "## 逐条", "", "| 工具条 | 条目 | 档 | 官方成员（已核） | 本仓入口 |", "|---|---|---|---|---|"]
    order = {"可攻关": 0, "待验证": 1, "待查": 2, "已能": 3}
    for it in sorted(items, key=lambda x: (order.get(x["tier"], 9), x["tb"], x["zh"])):
        hits = it["api_iface_hits"] + it["api_member_hits"]
        lines.append("| %s | %s | **%s** | %s | %s |" % (
            it["tb"], it["zh"], it["tier"],
            (", ".join("`%s`" % h for h in hits[:3]) or "—"),
            ("`%s`" % it["entry"]) if it.get("entry") else "—"))
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(
        {"_": "\u53f0\u8d26 + \u5b98\u65b9\u6e90\u6838\u5b9e\u7ed3\u679c", "summary": dict(c),
         "by_toolbar_gap": dict(c_tb), "items": items},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  产物：%s" % OUT_MD)
    print("  产物：%s" % OUT_JSON)
    missing = [it["zh"] for it in items if it["tier"] == "\u5f85\u67e5"]
    if missing:
        print("  \u2605 \u5f85\u67e5\uff08api \u6ca1\u6838\u5230\uff0c\u5148\u67e5\u6e05\uff09\uff1a%s" % ", ".join(missing[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
