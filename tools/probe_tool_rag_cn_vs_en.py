"""★ 中/英检索对照实验（离线，不碰 SolidWorks、不改任何文件）。

★ 回答两个问题（业主 2026-10-04 提问）：
  ① 同一批任务，用**中文**查 vs 用**英文**查，命中率差多少？⇒ 决定「要不要补中文关键词」
  ② ★★ 有些工具**名字本身有歧义** ⇒ 补关键词也救不回来？⇒ 量「**同族误选率**」

★ 三个查询族（★ 第三族不含我的措辞偏倚）：
  · CN        —— 中文说法（含业主本会话原话）
  · EN-nat    —— 英文自然说法（我写）
  · ★ EN-mech —— **从工具名机械反推**（去 `solidworks_` 前缀、下划线改空格）
                 ★ 这模拟「模型读了工具名之后会拿什么去搜」⇒ **无我的措辞偏倚** ✓

★ 判据：BM25 top-k 命中率 + 逐条排名 + **同族误选率**（top-1 落在同一前缀族里但不是期望工具）。
"""
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
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metric_scope as ms   # ★ 口径注册表（★ 事实 517：口径必须落成代码）
import register_capabilities as rc                                    # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")


def tok(text: str) -> list[str]:
    """★ CJK 二元组 + ASCII 词（★ 字符类**不含 `_`** ⇒ snake_case 会被切开）。"""
    text = text.lower()
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    out = re.findall(r"[a-z0-9]{2,}", text)
    cjk = "".join(ch for ch in text if CJK.match(ch))
    out += [cjk[i:i + 2] for i in range(len(cjk) - 1)]
    return out


def build():
    names, docs = [], []
    for s in rc.all_specs():
        params = " ".join(p.name for p in (getattr(s, "params", None) or []))
        toks: list[str] = []
        for field in (s.name, getattr(s, "title", "") or "", params,
                      getattr(s, "doc", "") or ""):
            toks += tok(field)
        names.append(s.name)
        docs.append(toks)
    return names, docs


def bm25(docs, k1=1.5, b=0.75):
    N = len(docs)
    avg = sum(len(d) for d in docs) / max(1, N)
    df = Counter()
    for d in docs:
        df.update(set(d))
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
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


#: ★ (中文说法, 英文自然说法, 期望工具) —— ★ 第一列含业主本会话原话
TASKS = [
    ("看零件的质心和体积", "check the part's mass properties and volume", "solidworks_part_mass_properties"),
    ("给选中边加圆角", "fillet the selected edge", "solidworks_fillet"),
    ("给边加倒角", "chamfer the selected edge", "solidworks_chamfer"),
    ("导出运动算例的 AVI 动画", "export the motion study to AVI", "solidworks_motion_export_avi"),
    ("把弹窗关掉", "close the modal dialogs", "solidworks_gui_close_modals"),
    ("算直边倒角切掉多少体积", "volume removed by a straight edge chamfer", "solidworks_chamfer_straight_edge_volume"),
    ("加一个压力载荷", "apply a pressure load", "solidworks_simulation_apply_pressure"),
    ("跑静力仿真求解", "run the static simulation analysis", "solidworks_simulation_run_analysis"),
    ("建网格但别把内存吃爆", "create the mesh without exhausting memory", "solidworks_simulation_create_mesh_safely"),
    ("把三个视图出成工程图", "create three standard drawing views", "solidworks_drawing_create_three_standard_views"),
    ("读成本分析的批量大小", "read the costing lot size", "solidworks_costing_read_analysis"),
    ("导出 STEP", "export the part to STEP", "solidworks_export_step"),
    ("装配体干涉检查", "check assembly interference", "solidworks_assembly_check_interference"),
    ("列装配体的组件清单", "list the assembly components", "solidworks_assembly_list_components"),
    ("读拉伸特征的深度", "read the extrude feature depth", "solidworks_extrude_depth"),
    ("建钣金基体法兰", "create the sheet metal base flange", "solidworks_sheet_metal_create_base_flange"),
    ("建钣金边线法兰", "create the sheet metal edge flange", "solidworks_sheet_metal_create_edge_flange"),
    ("焊件顶端盖", "weldment end cap", "solidworks_weldment_insert_end_cap"),
    ("拓扑优化建算例", "create a topology study", "solidworks_topology_create_study"),
    ("读文档单位是不是毫米", "read the document units", "solidworks_read_document_units"),
    ("在草图上画矩形", "draw a rectangle in the sketch", "solidworks_sketch_add_rectangle"),
    ("列所有配置", "list all configurations", "solidworks_inspect_configurations"),
    ("读零件包围盒", "get the part bounding box", "solidworks_part_bounding_box"),
    ("设置自定义属性", "set custom properties", "solidworks_set_custom_properties"),
]


def mech_en(tool: str) -> str:
    """★★ 从工具名机械反推英文查询 —— ★ 无我的措辞偏倚。"""
    return tool.removeprefix("solidworks_").replace("_", " ")


def family(tool: str) -> str:
    """★ 粗粒度"同族"键：去掉最后一段动作词。"""
    parts = tool.removeprefix("solidworks_").split("_")
    return "_".join(parts[:-1]) if len(parts) > 1 else tool


def main() -> int:
    names, docs = build()
    score = bm25(docs)
    ks = (1, 3, 5, 10)
    res: dict = {}
    for fam, key in (("CN", 0), ("EN-nat", 1), ("EN-mech", None)):
        hit = {k: 0 for k in ks}
        rows = []
        for t in TASKS:
            q = mech_en(t[2]) if key is None else t[key]
            ranked = score(q)
            idx = names.index(t[2]) if t[2] in names else None
            rank = next((r + 1 for r, (_s, i) in enumerate(ranked) if i == idx), None)
            top1 = names[ranked[0][1]] if ranked else ""
            #: ★ 同族误选：top-1 与期望工具同族但不是它
            mis = bool(top1) and family(top1) == family(t[2]) and top1 != t[2]
            for k in ks:
                if rank and rank <= k:
                    hit[k] += 1
            rows.append({"q": q, "want": t[2], "rank": rank, "top1": top1, "sibling_mis": mis})
        res[fam] = {"hit": hit, "rows": rows}
    n = len(TASKS)
    print("★ 中/英检索对照（BM25，433 个工具，%d 个任务）" % n)
    print()
    print(ms.block_for('bm25_topk'))
    print()
    print("| 查询族 | top-1 | top-3 | top-5 | top-10 |")
    print("|---|---:|---:|---:|---:|")
    for fam in ("CN", "EN-nat", "EN-mech"):
        h = res[fam]["hit"]
        print("| %-8s | %d/%d = %.0f%% | %d/%d = %.0f%% | %d/%d = %.0f%% | %d/%d = %.0f%% |"
              % (fam, h[1], n, 100.0 * h[1] / n, h[3], n, 100.0 * h[3] / n,
                 h[5], n, 100.0 * h[5] / n, h[10], n, 100.0 * h[10] / n))
    print()
    print("★ 逐条排名（★ 看哪些任务**三族都命不中** ⇒ 那是名字本身的问题）:")
    print()
    print("| 任务 | CN | EN-nat | EN-mech | 期望工具 |")
    print("|---|---:|---:|---:|---|")
    never_found = []
    for i, t in enumerate(TASKS):
        r = [res[f]["rows"][i]["rank"] for f in ("CN", "EN-nat", "EN-mech")]
        flag = " ★★" if all(x is None or x > 10 for x in r) else ""
        if flag:
            never_found.append(t[2])
        print("| %s | %s | %s | %s | `%s`%s |"
              % (t[0], r[0], r[1], r[2], t[2].removeprefix("solidworks_"), flag))
    print()
    print("★★ 三族**全部掉出 top-10** 的有 **%d** 个:" % len(never_found))
    for x in never_found:
        print("     %s" % x)
    print()
    mis_any = sum(1 for f in ("CN", "EN-nat", "EN-mech") for r in res[f]["rows"] if r["sibling_mis"])
    print("★ 同族误选（top-1 是它的兄弟）总次数：**%d** / %d" % (mis_any, 3 * n))
    out = ROOT / "output" / "tool-rag-cn-vs-en.json"
    out.write_text(json.dumps({"tasks": len(TASKS),
                               "summary": {f: res[f]["hit"] for f in res},
                               "never_found": never_found,
                               "rows": {f: res[f]["rows"] for f in res}},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 明细:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
