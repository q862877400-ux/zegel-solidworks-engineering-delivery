"""★ T1-1：从 C5 手核数据里**机械筛**出可信的「别名 → 工具」候选对。

★★ 为什么不能直接用他们的 `hits`：
  `c5-gap-handcheck.json` 的 `hits` 是**子串匹配**的产物 —— 例如 `bbox` 那条的 hits 里有
  `solidworks_toolbox_list_standards` / `solidworks_toolbox_load_index`（**米思米/标准件库工具**），
  只因 `toolbox` 里含 `box` ✓✗ 这正是对方 V1/V3 点名的「子串噪声」。

★ 本步骤的判据（★ 只做**可信性**筛，不做增益判断 —— 增益由下一步实测）：
  ★ 保留条件 = `op` 或它的某个 `key` **作为词**出现在目标工具的 **name 或 title** 里。
  ★★ 依据：别名要起作用，至少得与工具的**模型可见文本**同概念；
     若连名字/标题里都没有，那多半是子串命中，不是别名关系。
  ⚠ 本判据**偏保守** —— 它会漏掉「真别名但名字里没有」的情况（★ 那些留给第 ② 步实测捞）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                    # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = ROOT / "specs" / "204-bunny-moat-batches" / "recon" / "c5-gap-handcheck.json"

TOOL_WORD = re.compile(r"[a-z0-9]+")


def words(text: str) -> set:
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text or "")
    return set(TOOL_WORD.findall(t.lower()))


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    by_name = {s.name: s for s in rc.all_specs()}
    #: ★ 上游 server.py 的工具（不在 ToolSpec 里）—— 如实标出，不当成"不存在"
    upstream = {"solidworks_set_appearance", "solidworks_inspect_configurations",
                "solidworks_set_custom_properties"}

    kept, dropped_missing, dropped_substr = [], [], []
    for r in rows:
        if r.get("verdict") != "换名已有":
            continue
        op = str(r.get("op") or "")
        keys = [str(k) for k in (r.get("keys") or [])]
        cue = {op.lower()} | {k.lower() for k in keys}
        for hit in r.get("hits") or []:
            s = by_name.get(hit)
            if s is None:
                dropped_missing.append((op, hit, "本仓 ToolSpec 里没有（可能是上游工具）"))
                continue
            surf = words(s.name) | words(getattr(s, "title", "") or "")
            #: ★ 判据：cue 里有没有【整个词】出现在工具的 name/title 里
            if cue & surf:
                kept.append({"op": op, "keys": keys, "tool": hit,
                             "matched": sorted(cue & surf),
                             "title": getattr(s, "title", "") or "",
                             "is_upstream": hit in upstream,
                             "sources": r.get("sources") or []})
            else:
                dropped_substr.append((op, hit, "name/title 里没有该词 ⇒ 疑子串命中"))

    print("★ 输入: %s" % SRC.name)
    print("★ 「换名已有」行数: %d" % sum(1 for r in rows if r.get("verdict") == "换名已有"))
    print("★ 机械筛后保留 **%d** 对；丢掉 %d 对（子串疑云）+ %d 对（本仓没有该工具）"
          % (len(kept), len(dropped_substr), len(dropped_missing)))
    print()
    print("★★ 丢掉的「子串疑云」样例（★ 这就是 hits 不能直接信的证据）:")
    for op, hit, why in dropped_substr[:10]:
        print("   %-22s → %-46s %s" % (op, hit.removeprefix("solidworks_"), why))
    print()
    print("★ 保留的样例（前 12）:")
    for k in kept[:12]:
        print("   %-20s → %-44s 命中词=%s" % (k["op"], k["tool"].removeprefix("solidworks_"),
                                              ",".join(k["matched"])))
    print()
    print("★ 覆盖到的**不同工具**数: %d ；不同 op 数: %d"
          % (len({k["tool"] for k in kept}), len({k["op"] for k in kept})))
    out = ROOT / "output" / "t1-alias-candidates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"kept": kept,
                               "dropped_substring_suspect": [
                                   {"op": o, "tool": h, "why": w} for o, h, w in dropped_substr],
                               "dropped_missing_tool": [
                                   {"op": o, "tool": h, "why": w} for o, h, w in dropped_missing]},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 写出: %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
