"""★ T2-1/T2-2：从 534 条前置里**机械分出可机检的那些**（★ 会话/文档/选择/保存态）。"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
SRC = ROOT / "specs" / "204-bunny-moat-batches" / "recon" / "c3-merged.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 可机检：说的是**我们能在测试里断言的会话/文档/选择状态**
CHECKABLE = re.compile(
    r"(已运行|已连接|已打开|活动文档|活动装配|活动零件|当前文档|选中|选择|已保存|未保存|"
    r"命令锁|CommandInProgress|文档已|空文档|新建文档|active document|active assembly|"
    r"selected|selection|saved|connected|running|open|in progress)", re.I)
#: ★ 不可机检：说的是**外部工具链/人工操作** ⇒ 明确排除（★ 判据要写「不算什么」）
NOT_CHECKABLE = re.compile(
    r"(Visual Studio|Immediate|即时窗口|建好.*工程|工程文件|GUID|注册表|regasm|"
    r"宏里|录制宏|手工|手动|点击|菜单)", re.I)


def main() -> int:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for cap in d["results"]:
        for p in cap.get("preconditions") or []:
            if p.get("state") != "not_covered":
                continue                      #: ★ 只看未覆盖的
            t = p.get("text") or ""
            rows.append({"cap": cap["name"], "text": t, "from": p.get("from", ""),
                         "checkable": bool(CHECKABLE.search(t)) and not NOT_CHECKABLE.search(t),
                         "why_not": ("外部工具链/人工操作" if NOT_CHECKABLE.search(t)
                                     else ("" if CHECKABLE.search(t) else "没提到会话/文档/选择状态"))})
    nc = [r for r in rows if r["checkable"]]
    print("★ not_covered 前置: **%d** 条" % len(rows))
    print("   · ★ 可机检（提到会话/文档/选择/保存态，且不含外部工具链）: **%d**" % len(nc))
    print("   · 不可机检: %d（%s）"
          % (len(rows) - len(nc), dict(Counter(r["why_not"] for r in rows if not r["checkable"]))))
    print()
    print("★ 可机检的按能力分布（前 12）:")
    for cap, n in Counter(r["cap"] for r in nc).most_common(12):
        print("   %-34s %d" % (cap, n))
    print()
    print("★ 抽样（前 10 条可机检的）:")
    for r in nc[:10]:
        print("   [%s] %s" % (r["cap"][:22], r["text"][:88]))
    out = ROOT / "output" / "t2-preconditions-checkable.json"
    out.write_text(json.dumps({"n_not_covered": len(rows), "n_checkable": len(nc),
                               "checkable": nc,
                               "not_checkable": [r for r in rows if not r["checkable"]]},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ 写出: %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
