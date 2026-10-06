"""★ 规格 209 · B1 批：补齐/更正 capabilities.yaml（① idx 235+236 的判据修好 ② 追加 idx 209）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/amend_s209_b1_capabilities.py`
# 定位:   ★ 承 `tools/add_s209_b1_capabilities.py`（它追加了 B1 的头 4 条）。本次做两件事：
#   ① **更正** `session_rebuild` —— 它的"包围盒"判据第一版是**空转的**（读到了字典却按可迭代对象用
#      ⇒ 被 `except` 吞 ⇒ `bbox_changed` 恒 `False`）⇒ 本轮修好并**真机复验**，故把读数与控制原因
#      一起写进 evidence / limitations ✓
#   ② **追加** `move_copy_body`（idx 209）—— ★ 含本轮真机定出的两件事：
#      **长度是 mm（不是米）**、**官方参数名与实际作用轴 X↔Z 互换** ✓
#   ★★ 落盘纪律：`capabilities.yaml` 实测是 `json.dumps(indent=2, ensure_ascii=False)` 的**精确往返**
#      ⇒ 故本脚本**可以** load→改→dump（diff 极小）；★ 但仍先看 `git diff --stat` 是否有 deletions ✓
# 官方依据: 不适用（本脚本不碰 COM）；★ 每条能力的官方依据写在它自己的 `source_evidence` 里。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(r"D:\AI\SW\capabilities.yaml")

EVID = ("★★★ 真机（2026-10-06 · 规格 209 的 **B1 批**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_union_adopt_b1.py`")

SESSION_REBUILD_EVIDENCE = (
    EVID + " ⇒ ★ 三档逐档（100×60×20 的板，特征树 **7**）：`edit` / `force` / `all` "
           "**都 `ok=True`** · `needs_rebuild 0→0`（`fully_rebuilt`）· `tree 7→7` · "
           "**`bbox_comparable=True` 且前后读数逐位相同**"
           "（`[[-30.0, -20.0, -20.0], [30.0, 20.0, 0.0]]`，★ 两侧都是**真实读数** ⇒ 判据**非空转**）；"
           "★ 负例 `mode='nonsense'` **在入口被拒**（`未知的 mode 'nonsense'；合法：edit, force, all`）✓ "
           "★ 证据 `output/union-adopt-b1-evidence.json`（★ `output/` 被 gitignore ⇒ "
           "要复现就重跑那条命令）"
)

SESSION_REBUILD_VACUOUS = (
    "★★ **本能力的「包围盒」判据曾经是空转的（本轮自查抓到并已修）**："
    "`sw_part.get_bounding_box` 回的是**字典**，而第一版把它当可迭代对象写 ⇒ `float(\"min\")` 抛异常"
    "被 `except` 吞掉 ⇒ 回 `None` ⇒ **`bbox_changed` 永远 `False`** —— ★★ 判据**看着在、其实没在判** ✓ "
    "★ 修法两条：① 取对字段（`bb[\"min\"]`/`bb[\"max\"]`）；② 返回值里**显式给 `bbox_comparable`** —— "
    "★★ `None`（**读不到** ⇒ 判据不可用）与 `False`（**读了、没变**）**必须分得开**，"
    "否则「读不到」会被当成「没变」 ✓ ★ 已加回归测试（`test_rebuild_bbox_criterion_is_not_vacuous`）✓"
)

MOVE_COPY_BODY = {
    "id": "move_copy_body",
    "label": "移动 / 复制实体（`IFeatureManager::InsertMoveCopyBody2`，**12 参**）—— ★ 真机过，"
             "★ 并实测定死两件事：**长度是 mm 不是米**、**官方参数名与实际作用轴 X↔Z 互换**",
    "level": "verified",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        EVID + " 的 **T5 格** ⇒ ★ 60×40×20 板：`move_copy_body(doc, 'all', translate_x_mm=25.0)` ⇒ "
               "**`ok=True` · `moved=True`** · 包围盒 x `-30.0/30.0 → -5.0/55.0`（**正好 25 mm**）；"
               "★ `copy=True` ⇒ **实体 1→2**（`copied=True`）；★ **平移+旋转同给** ⇒ "
               "`both_given=True` 并带官方逐字（只应用旋转）；★ 负例 `index:99` ⇒ `ok=False` + "
               "`实体下标 99 越界`✓ ★ 证据 `output/union-adopt-b1-evidence.json`",
        EVID + " 的 **T5b 格（三格互证「旋转到底绕哪根轴」）** ⇒ ★ 判据是**哪一轴的跨度不变**："
               "只给 `rotate_angle_x_deg=30` ⇒ 跨度 `[60,40,20] → [60,44.641,37.3205]`（**x 不动**）"
               "⇒ 实际绕 **X**；只给 y ⇒ `[61.9615,40,47.3205]`（**y 不动**）⇒ 绕 **Y**；"
               "只给 z ⇒ `[71.9615,64.641,20]`（**z 不动**）⇒ 绕 **Z** ✓ "
               "★★ 且 z 那格的 `71.9615 = 60·cos30 + 40·sin30`、`64.641 = 60·sin30 + 40·cos30` "
               "**逐位吻合** ⇒ 同时证明「**收度、COM 侧弧度**」的换算正确 ✓",
        "★ 官方依据逐页读过（铁律 4）：`C:\\swapi\\types\\IFeatureManager\\InsertMoveCopyBody2.md`"
        "（12 参；`## Remarks` 两条逐字已落进实现：① 平移与旋转**不能同时生效**、同时给**只应用旋转**；"
        "② **逐字 mark 表 1/2/4/8**）· `C:\\swapi\\types\\IBody2\\Select2.md`"
        "（★ mark **不在形参里** —— 设在 `ISelectData` 上）· `ISelectionMgr\\CreateSelectData.md` · "
        "`ISelectData\\Mark.md` · `enums\\swBodyType_e.md`（`swAllBodies=-1`）· "
        "★★ **官方示例 `examples\\Move_Bodies_Example_VB.md` 给了「调用序」**"
        "（`ClearSelection2` → `GetBodies2` → `CreateSelectData` + `Mark=1` → `body.Select2(True,data)` "
        "→ `InsertMoveCopyBody2(...)`）—— ★ 本模块的 `_select_bodies` **就是照它写的** ✓",
    ],
    "limitations": [
        "★★ **官方页没写这几个长度参数的单位** ⇒ 真机定案：按**文档长度单位（mm）**解释 —— "
        "传 `25.0` 正好挪 25 mm；★ 而先按「COM 惯例=米」换算传 `0.025` **只挪 0.025** ⇒ "
        "★★ 那会是一个**静默的 1000× 错误**（工具回 `ok=True`，**而且它能过「包围盒变了」那条判据**）✓ "
        "⇒ ★ 本模块**原样传毫米、不做换算**，并把这条**随返回值**带出（`unit_findings`）✓",
        "★★ **同一个调用里角度是弧度**（长度是毫米 —— 一个接口**混两种口径**）：真机传 `30.0` "
        "得到约 **81°**（`30 rad ≡ 278.87° ≡ −81.1°`）⇒ ★ 本模块收**度**、在边界 `deg()` 换算一次 ✓",
        "★★★ **官方参数名与实际作用轴不一致：`RotAngleX` 实际绕 Z、`RotAngleZ` 实际绕 X**（`Y` 是对的）"
        "—— 官方页**没写**这件事；★ 由 T5b 三格互证定出 ⇒ ★★ 本模块**已按 `ROTATION_AXIS_MAP` "
        "补偿**，对外 `rotate_angle_x/y/z_deg` 的含义**就是「绕该轴转」**（★ 与名字一致）✓ "
        "★ 映射是**单源常量**：SW 哪天改了就只改那一个（★ 而 T5b 会当场红）✓",
        "⚠ **未验**：★ **三轴同时给**时的合成顺序（Euler 序）—— 官方没写、本轮也没测 ⇒ "
        "本模块**不承诺**那个语义 ✓",
        "★ `InsertMoveCopyBody2` 回的是 `IFeature` 指针，真机拿到 `<COMObject <unknown>>` ⇒ "
        "★ **它给不出判据** ⇒ 本模块用「包围盒变（移动）/ 实体个数增（复制）」两处**回读** ✓ "
        "⚠ **未验**：★ 旋转**只验了「只给一个轴、30°、RotPoint=(0,0,0)」**；"
        "★ 非原点旋转 / 绕选定参考实体（mark 2/4/8）**未验** ✓",
        "★ 选择器**只验了 `all` 与 `index:<n>`** 两种；★ 多个体 + 部分体的组合未验 ✓ "
        "⚠ 选择走官方示例的 `SelectData.Mark=1` + `IBody2.Select2`（★ 而 `mark` **不在** `Select2` 的形参里）——"
        "★ 本函数**会先 `ClearSelection2(True)`**（官方示例第①步）⇒ ★ **它会清掉调用方原有的选区**（使用纪律）✓",
    ],
    "source_evidence": "★ 本仓自建（按**官方签名 + `## Remarks` + 官方示例的调用序**立）："
                       "`C:\\swapi\\types\\IFeatureManager\\InsertMoveCopyBody2.md` · "
                       "`C:\\swapi\\types\\IBody2\\Select2.md` · `ISelectionMgr\\CreateSelectData.md` · "
                       "`ISelectData\\Mark.md` · `C:\\swapi\\enums\\swBodyType_e.md` · "
                       "官方示例 `Move_Bodies_Example_VB.md` —— ★ **逐页读过**（★ 例子给的是**调用序**，"
                       "签名与 Remarks 都给不出）✓ ★ 落点按裁决书 §九：本仓**没有**多体/布尔那一族 ⇒ "
                       "按铁律 3 在 `scripts/` 下新建 `sw_body_ops.py` ✓ "
                       "★ **不来自任何外部项目**（★ 且本轮实测定出两处外部项目照「惯例」必踩的坑）✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_part_move_copy_body"],
}


def main() -> int:
    text = CAPS.read_text(encoding="utf-8")
    data = json.loads(text)
    caps = data["capabilities"]

    #: ① 更正 session_rebuild
    hit = [c for c in caps if c.get("id") == "session_rebuild"]
    if len(hit) != 1:
        raise SystemExit("★ 找不到唯一的 session_rebuild（找到 %d 条）⇒ 停手" % len(hit))
    entry = hit[0]
    if "bbox_comparable" not in json.dumps(entry, ensure_ascii=False):
        entry["evidence"][0] = SESSION_REBUILD_EVIDENCE
        entry["limitations"].insert(0, SESSION_REBUILD_VACUOUS)
        print("★ 更正 session_rebuild：evidence[0] + limitations 各 1 条")
    else:
        print("★ session_rebuild 已更正过 ⇒ 跳过")

    #: ② 追加 move_copy_body
    if any(c.get("id") == "move_copy_body" for c in caps):
        print("★ move_copy_body 已存在 ⇒ 跳过")
    else:
        caps.append(MOVE_COPY_BODY)
        print("★ 追加 move_copy_body")

    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)                                            # ★ 先验证再落盘
    CAPS.write_text(out, encoding="utf-8")
    print("★ 现在 capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
