import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

ENTRY = {
    "id": "sketch_query",
    "label": "草图读回（ISketch 按类型取几何）",
    "level": "verified",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": ["2026"],
    "dependencies": ["SolidWorks", "pywin32"],
    "evidence": [
        "python tools/verify_sketch_getters_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画 1 条线 + 1 段弧 → "
        "逐个调取法 → 退草图 → 关件不保存，**17/17 通过**，"
        "证据落 output/sketch-getters-smoke-evidence.json）",
        "pytest tests/test_sw_sketch_contract.py（**12 条契约测试，无 COM**）",
    ],
    "limitations": [
        "⚑ 2026-10-01（轮 117）**新建条目并直接标 `verified`** —— "
        "★ 起因是**发现覆盖缺口**：`sw_sketch.py`（草图读回）此前**没有能力条目**"
        "（`sketch_edit_ops` 只管编辑）⇒ A1「每域都有来源」在这一处其实**是空的**。",
        "⚑ 真机证据：画 **1 条线 + 1 段弧** ⇒ `get_sketch_segments` 返回 **2**（线+弧，**交叉验证**）、"
        "`get_lines` 返回 **12** 个浮点、`get_arcs` 返回 **16**、`get_sketch_points` 返回 **5**、"
        "`get_ellipses`/`get_parabolas`/`get_user_points` 各 **0**（画的就是这些，合理）。"
        "⚠ **收尾无残留模态框**，临时件已关且未保存。",
        "★ **6 个取法在轮 111（`030`）刚从废弃入口换到后继** —— 本冒烟正是为**验那一次替换**而做的："
        "`GetLines2(swCrossHatchFilter_e)`（**唯一带参的后继**）/ `GetArcs2` / `GetEllipses3` / "
        "`GetParabolas2` / `GetSketchPoints2` / `GetUserPoints2` **全部真机可调**。",
        "⚠ **只证「没抛异常 + 元素数合理」**，**不证元素内容正确** —— 例如返回的浮点数组"
        "里坐标的排列顺序**未核**（官方 Remarks 说明过顺序，但本模块只做 `as_sequence` 转换）。",
        "⚠ 只测了**线 + 弧**两种几何；**椭圆 / 抛物线 / 样条 / 多段线 / 用户点**的真机取法**未测**"
        "（本次它们都返回 0 —— 因为没画）。",
        "⚠ `collect_sketch_evidence` / 变换类（`get_model_to_sketch_transform` 等）**未纳入本次冒烟**。",
        "`as_sequence` 只保证**拿到元素**，**不保证顺序**（官方未定义 SAFEARRAY 的顺序保证）。",
    ],
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "本项目自建；依据为出厂类型库反射的 `ISketch` 段与官方结构化文档"
                       "（见 `scripts/sw_sketch.py` 的来源块）。",
}

if any(c.get("id") == ENTRY["id"] for c in d["capabilities"]):
    print("  已存在")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已新增 sketch_query（verified）")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
