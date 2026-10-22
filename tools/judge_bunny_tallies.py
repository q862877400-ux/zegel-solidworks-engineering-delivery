"""★ 从（被截断的）workflow 返回体里榨出裁决口径：`verdict_tally` + `recommendation_tally` 分档。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/judge_bunny_tallies.py
# 定位:   ★ 主裁判工序的**降级版**。★★ 事故：workflow 的完整返回体（1.8 MB）被工具截断
#           ，落盘的溢出文件只有那一版截断文本 ⇒ **逐条 index→op→verdict 的映射丢了** ✓✗
#           ★★★ 根因是**我的 schema 设计错**：把该被机器判读的 `verdict` / `recommendati
#           on`  声明成普通 string ⇒ bunny 各写一整段散文 ⇒ ① 返回体超大被截断 ② JSON 非
#           法 ✓⇒ ★★ **定则（下一轮必守）**：**给机器读的字段一律 `enum` 或受长度约束的
#           短串**；  散文只许进**单独的** `notes` 字段，且那个字段**不进返回体**（写文
#           件由 bunny 自己做）✓
#         ★ 本脚本只做**能做的部分**：从 tally 的**键**里分档（键本身自描述，含 op 与结论）✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SPILL = Path(
    r"C:\Users\Zegel\AppData\Local\Temp\dsh-spill-jWMrNL\session-bf32b25314ff"
    r"\0d5af33ae392-workflow.txt"
)

VERDICT_RULES = [
    ("已有等价物", ("已有等价物", "已有等价", "不是缺口", "重复实现", "重实现")),
    ("真缺口", ("真缺口", "没有等价物", "确实没有")),
    ("查不到", ("查不到", "语义不明", "不存在")),
]
REC_RULES = [("采纳", ("建议采纳",)), ("缓办", ("建议缓办",)), ("不做", ("建议不做",))]


def block(text: str, name: str) -> str:
    m = re.search(r'"%s"\s*:\s*\{' % name, text)
    if not m:
        return ""
    depth, start = 0, m.end() - 1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]  #: ★ 被截断 ⇒ 回剩下的全部（后面按行解析，能捞多少算多少）


def classify(text: str, rules):
    for label, keys in rules:
        for k in keys:
            if k in (text or ""):
                return label
    return "(未归类)"


def main() -> int:
    raw = SPILL.read_text(encoding="utf-8", errors="replace")
    print("★ 溢出文本 %d 字符（**被截断**，逐条映射已丢）" % len(raw))

    for name, rules, title in (
        ("verdict_tally", VERDICT_RULES, "verdict（判定）"),
        ("recommendation_tally", REC_RULES, "recommendation（建议）"),
    ):
        blk = block(raw, name)
        #: ★ 容错：按行捞 `"……": N`（键可能是被截断的长串）
        pairs = re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*(\d+)', blk)
        tally: dict[str, int] = {}
        for key, n in pairs:
            tally[classify(key, rules)] = tally.get(classify(key, rules), 0) + int(n)
        print("\n=== %s ===" % title)
        for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
            print("   %-10s %3d" % (k, v))
        print("   合计 %d" % sum(tally.values()))
        if name == "recommendation_tally":
            print("\n   ★ 含「建议采纳」的原文（主裁判要逐条读）：")
            for key, n in pairs:
                if "建议采纳" in key:
                    print("     · %s" % key.replace("\\n", " ")[:230])
        if name == "verdict_tally":
            print("\n   ★ 判为「真缺口」的原文：")
            for key, n in pairs:
                if classify(key, VERDICT_RULES) == "真缺口":
                    print("     · %s" % key.replace("\\n", " ")[:210])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
