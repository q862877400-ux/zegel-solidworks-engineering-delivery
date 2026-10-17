"""★ 容错抽取 bunny 记录（溢出文件的 JSON 坏了 ⇒ 按字段正则捞，不靠整体 json 解析）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/judge_bunny_records.py
# 定位:   ★ 主裁判工序。★★ **事故与教训**：workflow 的返回体存进溢出文件后 `json.loads` **失败**
#           （先是 `Invalid control character`、`strict=False` 后变 `Unterminated string`）——
#           根因是**我在 workflow 的 schema 里把该被机器判读的字段（verdict / recommendation）
#           声明成了普通 string** ⇒ bunny 把它们写成一整段带引号与换行的散文 ⇒ ★ 返回体不再是合法 JSON ✓✗
#           ⇒ ★★ **判据**：**给机器读的字段必须是 enum 或受长度约束的短串**（本脚本只能补救，
#             下一轮派活**必须**在 schema 里用 `enum` 限死 ✓
#         ★ 本脚本因此改为**按字段正则容错抽取**：只要 `"index": N` 与 `"op": "..."` 还在，
#           就按记录边界切开，再逐字段捞 ✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPILL = Path(r"C:\Users\Zegel\AppData\Local\Temp\dsh-spill-jWMrNL\session-bf32b25314ff"
             r"\0d5af33ae392-workflow.txt")

#: ★ 记录边界：`"index": N`（后面紧跟 "op"）
REC_SPLIT = re.compile(r'"index"\s*:\s*(\d+)\s*,\s*"op"\s*:\s*"([^"]*)"')


def field(chunk: str, name: str, cap: int = 200) -> str:
    """★ 捞一个字段的**起始片段**（容错：允许字段里有引号与换行 ⇒ 取到下一个 key 之前）。"""
    m = re.search(r'"%s"\s*:\s*"(.*?)(?<!\\)"\s*,\s*"[a-z_]+"\s*:' % name, chunk, re.S)
    if not m:
        return ""
    return m.group(1).replace("\\n", " ")[:cap]


VERDICT_RULES = [
    ("已有等价物", ("已有等价物", "已有等价", "不是缺口", "重复实现", "重实现")),
    ("真缺口", ("真缺口", "没有等价物", "确实没有")),
    ("查不到", ("查不到", "语义不明", "不存在")),
]
REC_RULES = [("采纳", ("建议采纳",)), ("缓办", ("建议缓办",)), ("不做", ("建议不做",))]


def classify(text: str, rules):
    for label, keys in rules:
        for k in keys:
            if k in (text or ""):
                return label, k
    return "(未归类)", ""


def main() -> int:
    raw = SPILL.read_text(encoding="utf-8", errors="replace")
    print("★ 溢出文件 %d 字符" % len(raw))

    marks = list(REC_SPLIT.finditer(raw))
    print("★ 认出记录边界：**%d** 条" % len(marks))

    rows = []
    for i, m in enumerate(marks):
        start = m.start()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        chunk = raw[start:end]
        v_raw = field(chunk, "verdict")
        r_raw = field(chunk, "recommendation")
        v, vk = classify(v_raw, VERDICT_RULES)
        r, rk = classify(r_raw, REC_RULES)
        rows.append({
            "index": int(m.group(1)), "op": m.group(2),
            "domain": field(chunk, "domain", 40),
            "verdict": v, "verdict_head": v_raw[:120],
            "rec": r, "rec_head": r_raw[:120],
            "confidence": field(chunk, "confidence", 30),
            "official_member": field(chunk, "official_member", 70),
            "risks_head": field(chunk, "risks", 110),
        })

    worth = [x for x in rows if x["verdict"] == "真缺口" and x["rec"] == "采纳"]
    defer = [x for x in rows if x["verdict"] == "真缺口" and x["rec"] == "缓办"]
    reject = [x for x in rows if x["verdict"] == "已有等价物"]
    unk = [x for x in rows if x["verdict"] == "(未归类)" or x["rec"] == "(未归类)"]

    def dump(title, items, cap=60):
        print("\n=== %s（%d 条）===" % (title, len(items)))
        for x in items[:cap]:
            print("  #%-3s %-26s %-18s %-6s %s" % (x["index"], x["op"], x["domain"],
                                                   x["rec"], x["official_member"]))

    dump("★★ 真缺口 × 建议采纳（**值得排活**）", worth)
    dump("真缺口 × 建议缓办", defer, 30)
    dump("①已有等价物（**驳回**：不要重复实现）", reject, 60)
    dump("②查不到 / 未归类（**请裁判自己读**）", unk, 30)

    out = ROOT / "output" / "bunny-round1-judgement-table.json"
    out.write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n★ 已写：%s" % out)
    print("★ 合计：采纳 %d · 缓办 %d · 已有等价物 %d · 未归类 %d · 总 %d"
          % (len(worth), len(defer), len(reject), len(unk), len(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
