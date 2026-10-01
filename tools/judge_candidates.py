"""把 51 个候选族逐个判一遍：**它对应什么用户动作？**

方法（2026-10-01 轮 213）：
  ① 官方**示例**的标题里往往直接写着"拿这个接口干什么" —— 例如
     `Rotate_Assembly_Component_on_Axis_Example_CSharp.htm` 的标题是
     「Rotate Assembly Component on Axis Using IDragOperator::Drag Example」
     ⇒ ★ 那就直接告诉我们：`IDragOperator` 对应「**旋转装配体零件**」这个用户动作。
  ② 没有示例的，看它是否只出现在**属性列表**里（⇒ 数据查询，不是动作）。
  ③ ★ 判不出来的一律标「说不准」，**不编**。

⚠ 本脚本**只读**官方文档（`D:\\AI\\SW\\AI Solidworks\\官方文档\\`），产物落 `D:\\AI\\SW\\output\\`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\judge_candidates.py
# 定位:   回答「那 51 个候选族里，哪些对应真实用户动作（值得做）」——
#         用官方**示例标题**判，取代形态统计（形态统计已实测无判别力）。
# 官方依据: `D:\\AI\\SW\\AI Solidworks\\官方文档\\`（CHM 解包，随安装自带）
# 许可:   本仓库 MIT。官方文档随安装自带，无许可风险。
# ⚠ 只做静态阅读，不连 SolidWorks。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DOCS = Path(r"D:\AI\SW\AI Solidworks\官方文档")
CAND = Path(r"D:\AI\SW\output\candidate-51.json")
OUT = Path(r"D:\AI\SW\output\candidate-51-judged.json")

TAG = re.compile(r"<[^>]+>")


def text_of(p: Path, limit: int = 4000) -> str:
    raw = p.read_text(encoding="utf-8", errors="replace")[:limit]
    return html.unescape(TAG.sub(" ", raw))


def main() -> int:
    d = json.loads(CAND.read_text(encoding="utf-8"))
    pool = [r["family"] for r in d["with_source"] + d["without_source"]]

    #: 一次性把「示例文件」的标题建成索引（示例文件名里带 Example）
    ex_files = [p for p in DOCS.rglob("*Example*") if p.is_file()]
    print("  官方示例文件: %d 个" % len(ex_files))
    ex_titles = []
    for p in ex_files:
        t = text_of(p, 3000)
        #: 标题般的第一句（示例页开头就是「Xxx Example (C#)」）
        m = re.search(r"([A-Z][^.\n]{10,120}Example[^.\n]{0,20})", t)
        ex_titles.append((p.name, (m.group(1).strip() if m else p.stem).replace("  ", " ")))
    print("  已抽取标题: %d 条" % len(ex_titles))

    judged = []
    for iface in pool:
        hits = [(n, ti) for n, ti in ex_titles if iface in ti or iface in n]
        #: 也搜一下正文（有些示例页不把接口名写进标题）
        if not hits:
            for p in ex_files:
                try:
                    if iface in p.read_text(encoding="utf-8", errors="replace"):
                        t = text_of(p, 2500)
                        m = re.search(r"([A-Z][^.\n]{10,120}Example[^.\n]{0,20})", t)
                        hits.append((p.name, (m.group(1).strip() if m else p.stem)))
                        if len(hits) >= 3:
                            break
                except Exception:
                    pass
        judged.append({
            "iface": iface,
            "examples": [ti for _n, ti in hits[:3]],
            "verdict": "★ 有官方示例 ⇒ 有真实用法" if hits else "无示例 ⇒ 疑为数据/查询接口",
        })

    OUT.write_text(json.dumps(judged, ensure_ascii=False, indent=2), encoding="utf-8")
    with_ex = [j for j in judged if j["examples"]]
    print("")
    print("  ── 51 个候选：有官方示例（≈ 有真实用法）的 **%d 个** ──" % len(with_ex))
    for j in with_ex:
        print("    %-46s %s" % (j["iface"], j["examples"][0][:70]))
    print("")
    print("  ── 没有官方示例的 **%d 个**（多数应是数据/查询接口）──" % (len(judged) - len(with_ex)))
    print("    " + ", ".join(j["iface"] for j in judged if not j["examples"])[:900])
    print("")
    print("  产物:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
