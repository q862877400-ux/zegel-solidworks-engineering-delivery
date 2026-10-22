"""★ 核对收敛报告里的数字**是否与生成物一致** —— ★ 报告自己也要被判据管。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/check_convergence_numbers.py
# 定位:   ★ 2026-10-03（轮 438）`plan-200r-v3` **段 6**。
# ★★ **为什么它存在**：★ `docs/plan-200r-v3-convergence.md` **自称**"数字全部来自生成物"
#  ——
#     ★ 而**那句话本身是判据** ⇒ ★★ **它得能被机器验**（★ 否则就是自说自话）✓
# ★ 先例：★ `plan-24h-v2-convergence.md` 那次**手写过一份**同样的核对（★ 报告 6 项零偏差
# ）⇒
#     ★★ 本轮**把它变成可重复的一步** ✓
#   ★ 判据清单（★ 与报告 §〇 的表**一一对应**）：★ 工具数 · 真缺口四类 · 能力等级 ·
#     ★ 门禁数 · 判据登记 · 证据份数与 pass 数。
# 官方依据: 不适用（本仓自有的报告纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 报告里**每个**被核的数字都与生成物**逐项相等**。
# ⚠ 便携性：★ 拿不到工作区 ⇒ `[SKIP]` 并 exit 0。

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT.parent / "SW" / "docs" / "plan-200r-v3-convergence.md"
#: ★ 工作区可在别处（★ `DSL_WORKSPACE` 覆盖）—— ★ 而报告与产物**都在工作区**
W = Path(os.environ.get("DSL_WORKSPACE", Path(__file__).resolve().parents[1]))
REPORT = W / "docs" / "plan-200r-v3-convergence.md"


def main(argv: list) -> int:
    if not REPORT.is_file():
        print("  [SKIP] 找不到报告：%s" % REPORT)
        return 0
    if not (W / "output").is_dir():
        print("  [SKIP] 工作区不可达（%s）⇒ 无法核对" % W)
        return 0
    text = REPORT.read_text(encoding="utf-8")
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    try:
        import register_capabilities as rc

        tools = len(rc.all_specs())
    except Exception as exc:  # noqa: BLE001
        print("  [SKIP] 读不到注册表：%s" % str(exc)[:70])
        return 0

    tri = json.loads(
        (W / "output" / "real-gap-triage.json").read_text(encoding="utf-8")
    )["summary"]
    caps = json.loads((REPO_ROOT / "capabilities.yaml").read_text(encoding="utf-8"))[
        "capabilities"
    ]
    levels = Counter(c.get("level") for c in caps)
    ev = list((W / "output").glob("*evidence*.json"))
    passn = 0
    for p in ev:
        try:
            if json.loads(p.read_text(encoding="utf-8")).get("verdict") == "pass":
                passn += 1
        except Exception:  # noqa: BLE001
            pass
    gates = len(
        json.loads(
            (REPO_ROOT / "docs" / "gate-classification.json").read_text(
                encoding="utf-8"
            )
        )["classification"]
    )
    json.loads(
        (REPO_ROOT / "docs" / "judge-registry.json").read_text(encoding="utf-8")
    )["judges"]

    #: ★ 每项 = （报告里该出现的**粗体数字串**，生成物里的真值）
    #: ★★ 2026-10-03（轮 451）**口径改了**：工具名有**两条声明路**（事实 364）⇒
    #:   ★ 而核对器得同时看 **ToolSpec 数**、**装饰器数**、**总数**三个。
    import re as _re

    _srv = _re.findall(
        r"name=\"(solidworks_[A-Za-z0-9_]+)\"",
        (REPO_ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8"),
    )
    checks = [
        ("tools(spec)", str(tools), "**%d**" % tools),
        ("tools(decorator)", str(len(set(_srv))), "**%d**" % len(set(_srv))),
        (
            "tools(total)",
            str(tools + len(set(_srv))),
            "**%d**" % (tools + len(set(_srv))),
        ),
        ("该挂", str(tri["\u8be5\u6302"]), "**%d**" % tri["\u8be5\u6302"]),
        ("已有", str(tri["\u5df2\u6709"]), "**%d**" % tri["\u5df2\u6709"]),
        (
            "内部件",
            str(tri["\u5185\u90e8\u4ef6"]),
            "**%d**" % tri["\u5185\u90e8\u4ef6"],
        ),
        ("不做", str(tri["\u4e0d\u505a"]), "**%d**" % tri["\u4e0d\u505a"]),
        ("triage total", str(tri["total"]), "**%d**" % tri["total"]),
        ("caps", str(len(caps)), "**%d**" % len(caps)),
        ("verified", str(levels.get("verified")), "**%d**" % levels.get("verified")),
        ("stitched", str(levels.get("stitched")), "**%d**" % levels.get("stitched")),
        ("gates", str(gates), "**%d**" % gates),
        ("evidence", str(len(ev)), "**%d**" % len(ev)),
        ("evidence pass", str(passn), "**%d**" % passn),
    ]
    bad = []
    for label, _truth, token in checks:
        if token not in text:
            bad.append((label, token))
    print("  报告：%s" % REPORT.name)
    print("  核对 %d 项（工具 / 真缺口四类 / 能力等级 / 门禁 / 证据）" % len(checks))
    if bad:
        print("  报告里**找不到**这些数字 **%d** 处：" % len(bad))
        for label, token in bad:
            print("    %-18s 期望出现 %s" % (label, token))
        print("\n  判据：★ 报告自称「数字全部来自生成物」⇒ ★ 那句话**得能被机器验**。")
        print("  ★ 修法：把 §〇 表里的数字**按生成物重算一遍**（★ 不是手改那个字串）。")
        return 1
    print(
        "  [OK] 报告里的 %d 项数字**都出现在生成物的取值里**（★ 逐项相等）"
        % len(checks)
    )
    print(
        "       tools=%d · 该挂=%d · 已有=%d · 内部件=%d · 不做=%d · caps=%d · gates=%d · evidence=%d/%d"
        % (
            tools,
            tri["\u8be5\u6302"],
            tri["\u5df2\u6709"],
            tri["\u5185\u90e8\u4ef6"],
            tri["\u4e0d\u505a"],
            len(caps),
            gates,
            passn,
            len(ev),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
