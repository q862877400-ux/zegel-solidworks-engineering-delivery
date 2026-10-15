import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

LIM_1 = ("★ 只在空白新图纸上真机验证过；有视图的真实图纸与多图纸工程图未验证"
         "（list_views 的有视图路径、sheets_summary 的多图纸路径未验）")
LIM_2 = "工程图的写操作（加视图 / 标注 / 表格 / BOM）不在本能力内"
LIM_3 = ("★ 与 solidworks_inspect_drawing 分工不同、不重叠：那个要 drawing_path、自己开件、"
         "出三视图预览并落 JSON 报告；本能力只看当前活动文档、不落文件")
LIM_4 = ("★ 两个真机坑已处理：① ISheet.GetProperties2 给的是 8 个 double"
         "（官方 GetProperties 文档写 7 个），宽高单位是米 ⇒ 换算成毫米；"
         "② 空图纸上 GetFirstView() 返回的是图纸本身（Type == 1）⇒ 已过滤，否则会列出假视图")

EV_1 = ("python tools/capture_drawing_query_evidence.py（真机，2026-10-01 轮 224 / 砌墙 W2："
        "新建空工程图 ⇒ 三个读数 + 在零件上的负例 + 返回结构不足的负例，verdict: pass，"
        "证据落 output/drawing-query-evidence.json）"
        "—— ★ 关键正例：空图纸上 list_views 回空表（证明假视图被过滤）。")
EV_2 = ("python tools/probe_drawing_object_routes.py（真机探针，定下三个未知："
        "model.GetType()==3 且 GetCurrentSheet() 能直接调 · GetProperties2 是 8 个 double · "
        "空图纸 GetFirstView() 回的是图纸本身；证据 output/drawing-object-routes.json）")
EV_3 = ("pytest tests（全量 0 failed，含两个「钉死数量」守卫已同步：all_specs() 65 / 协议层 110）")

ENTRY = {
    "id": "drawing_current_sheet_query",
    "label": "工程图当前图纸的轻量只读读数（几张纸 / 图幅 / 视图清单）",
    "level": "verified",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": ["2026"],
    "dependencies": ["solidworks"],
    "limitations": [LIM_1, LIM_2, LIM_3, LIM_4],
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "evidence": [EV_1, EV_2, EV_3],
    "source": "original",
    "source_evidence": ("scripts/sw_drawing_query.py（照官方 IDrawingDoc/ISheet/IView 成员与官方示例 "
                        "Get_Drawing_View_Names_and_Types_Example_CSharp 新写）"),
}

ids = {c.get("id") for c in d["capabilities"]}
if "drawing_current_sheet_query" in ids:
    print("  已存在，跳过")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 已加能力条目 drawing_current_sheet_query")

d2 = json.loads(P.read_text(encoding="utf-8"))
print("  条目总数: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
