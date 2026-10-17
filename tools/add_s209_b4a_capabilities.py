"""★ 规格 209 · B2-4（idx 175 blank_sketch）：把 `sketch_visibility` 能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b4a_capabilities.py`
# 定位:   ★ 追加 **1 条**能力 `sketch_visibility`（隐藏/显示**选中的**草图 + 可见性回读）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(Path(__file__).resolve().parents[1] / "capabilities.yaml")

ENTRY = {
    "id": "sketch_visibility",
    "label": "草图可见性（`IModelDoc2::BlankSketch` / `UnblankSketch` + "
             "`IFeature::Visible` 回读）—— ★ 真机双向过",
    "level": "verified",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        "★★★ 真机（2026-10-06 · 规格 209 的 **B2-4** · idx **175**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b2_blank_sketch.py` ⇒ "
        "新建零件 + 两张草图，按**名字**选中 `草图1` ⇒ "
        "① `set_sketch_blanked(blank=True)` ⇒ **`ok=True`** · `IFeature::Visible` 回读 "
        "**`shown`(2) → `hide`(1)**；② `blank=False` ⇒ **`ok=True`** · **`hide`(1) → `shown`(2)**；"
        "③ 负例（名字不存在）⇒ 选区计数 **0** + **大声报** ✓ "
        "★ 证据 `output/spec209-blank-sketch.json`（★ `output/` 被 gitignore ⇒ 重跑那条命令即可）",
        "★★ **本条解决的是裁决书点名的那个真风险**：「怎么回读「隐藏了没有」」—— "
        "★ 官方 `BlankSketch` 回 `void`、那页**既无 Returns 也无 Remarks**，"
        "★ 官方示例的判据**只有肉眼**（逐字「Examine the graphics area」）⇒ "
        "★★ 本仓真机**定出了那个回读入口**：**`IFeature::Visible`**（`System.int Visible {get;}`）"
        "→ `swVisibilityState_e` ✓",
        "★ 官方依据逐页读过：`C:\\swapi\\types\\IModelDoc2\\{BlankSketch,UnblankSketch}.md`"
        "（都零参回 `void`；★ `BlankSketch` 摘要逐字「Hides the **selected** sketches」）· "
        "`C:\\swapi\\types\\IFeature\\Visible.md` · `C:\\swapi\\enums\\swVisibilityState_e.md`"
        "（Hide=1 · Shown=2 · Unknown=3，**没有 0**）· "
        "`C:\\swapi\\examples\\Hide_and_Show_Sketches_Example_VB.md`（★ **调用序**：先在树/图形区"
        "选中草图，再 `BlankSketch`；显示同样要先选中）",
    ],
    "limitations": [
        "★★★ **官方语义是「选中的草图」—— 本仓不实现、也不叫「hide all」**（裁决书硬约束）："
        "别家把它叫 `hide_all_sketches`，★ 那**是自己许的语义**（官方成员名与摘要里都没有 all），"
        "★ 而它的实现是「**零选区 + 返回常量**」—— ★★ **规则 6 的反例**"
        "（返回常量不是判据）⇒ ★ 本仓工具名 `solidworks_sketch_set_blanked`（动词用官方的 Blank、"
        "**不承诺 all**），★ 并加静态断言钉住（名字里不许出现 `all`）✓",
        "★ `IFeature::Visible` 是**只读**属性 ⇒ ★ 本仓**只能**用它**回读**，"
        "**不能**用它设可见性（★ 改可见性只有 `BlankSketch`/`UnblankSketch` 这条官方路）✓",
        "★ **读不到 ≠ 没变**：`feature_visibility` 读不到时回 `{raw: None, readable: False}`，"
        "★ **不冒充** `unknown`(3)；★ 判据只在**两次都读得到且值真的变了**时才 `ok=True` ✓",
        "⚠ **未验**：★ 只验了**零件**上的草图（装配/工程图里的草图**未验**）· "
        "★ 只验了**按名字**选（`__current_selection__` 那条路要调用方自己先选好，"
        "★ 本仓探针没有覆盖「交互式已选中」那种前置）· ★ 多选（一次选多张草图）**未验** ✓",
    ],
    "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序**立）："
                       "`C:\\swapi\\types\\IModelDoc2\\{BlankSketch,UnblankSketch}.md` · "
                       "`C:\\swapi\\types\\IFeature\\Visible.md` · "
                       "`C:\\swapi\\enums\\swVisibilityState_e.md` · "
                       "官方示例 `Hide_and_Show_Sketches_Example_VB.md` —— ★ **逐页读过** ✓ "
                       "★ 落点 `scripts/sw_sketch.py`（已有模块，铁律 3）· "
                       "★ **不来自任何外部项目**（★ 而本条的**反例**恰恰是别家那个名字）✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_sketch_set_blanked"],
}


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已存在 ⇒ 跳过")
    else:
        caps.append(ENTRY)
        print("★ 追加 sketch_visibility")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
