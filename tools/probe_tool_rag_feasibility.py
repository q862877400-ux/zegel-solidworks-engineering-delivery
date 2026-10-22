"""★ 可行性实验：**在本仓 433 个工具上内建一个检索（BM25）**，用真实任务查询量命中率。

★ 为什么做它（2026-10-04 · 业主问「塞个内置 rag 专门用来查工具可不可行」）：
  · 行业口径说"要按需发现"，但**没人给你本仓的数字** ⇒ 本脚本给数字 ✓
  · 判据：**给定一句真实任务描述，正确的工具在不在 top-5 / top-10** 里
    （★ 对照：论文 arXiv:2605.24660 在 BFCL(370 工具) 上"展示 7 个 ≈ 展示 50 个"；
      Claude Code 每次搜索默认只加载 **5** 个 ⇒ **top-5 就是现实的门槛**）✓
★ 实现说明：**零第三方依赖**（不装 rank_bm25）；★ **中文按字符二元组切**（CJK 无空格，
  朴素的按空格切会把整句当成一个词 ⇒ 那是假阴性陷阱）；ASCII 按词切 ✓
★ 如实标注：这是**离线检索质量**的实验，**不是**端到端 agent 效果的实验（后者要真跑模型）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/probe_tool_rag_feasibility.py
# 定位:   可行性实验：**在本仓 433 个工具上内建一个检索（BM25）**，用真实任务查询量命
#           中率。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")


def tok(text: str) -> list[str]:
    """★ 中文用**字符二元组**、ASCII 用词 —— ★ CJK 无空格，这是必需的。

    ★★★ 2026-10-04 修（★ 由 DeepSeek 调研路指出，我原先这版**有致命 bug**）：
      · ✗ 旧：`re.findall(r"[a-z0-9_]{2,}", text)` —— ★ **字符类里含 `_`** ⇒
        把 `solidworks_part_mass_properties` **整条当成一个词元** ⇒
        ★★ 于是**最强的字段（工具名）对词级查询完全失效**，
        而「40%」那个数字就是这么做出来的 ⇒ ★ **该数字不成立** ✓
      · ✓ 新：先按 `_` 与 camelCase **切开**，再取词 ⇒ `solidworks / part / mass / properties` ✓
      · ✗ 旧：把 CJK **单字**也加进词表 ⇒ 噪声（任何中文查询都命中所有工具）✓ 已去掉
      · ✗ 旧：二元组是从**整段拼接文本**上建的 ⇒ 跨字段边界产生**伪二元组** ✓
        ✓ 新：**按字段**分别建二元组（见 `build_docs`）✓
    """
    text = text.lower()
    out: list[str] = []
    #: ★ 驼峰切：`massProperties` → `mass properties`
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    #: ★★ ASCII 词：**字符类不含 `_`** ⇒ snake_case 自然被切开 ✓
    out += re.findall(r"[a-z0-9]{2,}", text)
    #: ★ CJK 二元组（**不**再加单字）
    cjk = "".join(ch for ch in text if CJK.match(ch))
    out += [cjk[i : i + 2] for i in range(len(cjk) - 1)]
    return out


def build_docs():
    """★ 每个工具一份词表 —— ★★ **按字段分别分词**，避免跨字段伪二元组（本轮修的第 3 处）。"""
    docs, names = [], []
    for s in rc.all_specs():
        params = " ".join(p.name for p in (getattr(s, "params", None) or []))
        toks: list[str] = []
        for field in (
            s.name,
            getattr(s, "title", "") or "",
            params,
            getattr(s, "doc", "") or "",
        ):
            toks += tok(field)  #: ★ 逐字段 → 不跨界
        docs.append(toks)
        names.append(s.name)
    return names, docs


def bm25(docs, k1=1.5, b=0.75):
    n_ = len(docs)
    avg = sum(len(d) for d in docs) / max(1, n_)
    df = Counter()
    for d in docs:
        df.update(set(d))
    idf = {t: math.log(1 + (n_ - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    tfs = [Counter(d) for d in docs]

    def score(q: str):
        qt = tok(q)
        out = []
        for i, tf in enumerate(tfs):
            dl = len(docs[i])
            s = 0.0
            for t in qt:
                f = tf.get(t, 0)
                if not f:
                    continue
                s += idf.get(t, 0.0) * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avg))
            out.append((s, i))
        out.sort(reverse=True)
        return out

    return score


#: ★ 20 条**真实任务查询**（★ 期望工具是我按本仓域写的；★ 拿不准的不写进来 —— 别自欺）
QUERIES = [
    ("导出运动算例的 AVI 动画", "solidworks_motion_export_avi"),
    ("把弹窗关掉 / 检查有没有弹窗", "solidworks_gui_close_modals"),
    ("算直边倒角切掉多少体积", "solidworks_chamfer_straight_edge_volume"),
    ("看零件的质心和体积", "solidworks_part_mass_properties"),
    ("加一个压力载荷", "solidworks_simulation_apply_pressure"),
    ("跑静力仿真求解", "solidworks_simulation_run_analysis"),
    ("建网格但别把内存吃爆", "solidworks_simulation_create_mesh_safely"),
    ("把三个视图出成工程图", "solidworks_drawing_create_three_standard_views"),
    ("读成本分析的批量大小", "solidworks_costing_read_analysis"),
    ("导出 STEP", "solidworks_export_step"),
    ("装配体干涉检查", "solidworks_assembly_check_interference"),
    ("列装配体的组件清单", "solidworks_assembly_list_components"),
    ("读拉伸特征的深度", "solidworks_extrude_depth"),
    ("给选中边加圆角", "solidworks_fillet"),
    ("建钣金基体法兰", "solidworks_sheet_metal_create_base_flange"),
    ("顶端盖（焊件）", "solidworks_weldment_insert_end_cap"),
    ("拓扑优化建算例", "solidworks_topology_create_study"),
    ("读文档单位是不是毫米", "solidworks_read_document_units"),
    ("设置文档外观颜色", "solidworks_set_appearance"),
    ("在草图上画矩形", "solidworks_sketch_add_rectangle"),
]


def main() -> int:
    names, docs = build_docs()
    score = bm25(docs)
    ks = (1, 3, 5, 10, 20)
    hit = {k: 0 for k in ks}
    rows = []
    for q, want in QUERIES:
        ranked = score(q)
        idx = names.index(want) if want in names else None
        rank = next((r + 1 for r, (_s, i) in enumerate(ranked) if i == idx), None)
        for k in ks:
            if rank and rank <= k:
                hit[k] += 1
        rows.append(
            {
                "query": q,
                "want": want,
                "rank": rank,
                "top5": [names[i] for _s, i in ranked[:5]],
            }
        )
        print(
            "  %-24s 期望 %-46s rank=%s"
            % (q[:22], want.removeprefix("solidworks_"), rank)
        )
    n = len(QUERIES)
    print()
    print("★ 命中率（离线 BM25，433 个工具，%d 条真实查询）:" % n)
    for k in ks:
        print("     top-%-3d **%2d/%d = %5.1f%%**" % (k, hit[k], n, 100.0 * hit[k] / n))
    out = ROOT / "output" / "tool-rag-feasibility.json"
    out.write_text(
        json.dumps(
            {"n": n, "hits": {str(k): hit[k] for k in ks}, "queries": rows},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print("★ 明细已写:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
