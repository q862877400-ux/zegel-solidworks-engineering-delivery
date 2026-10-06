"""★ 规格 209 · B3-1：把 idx 115+145（edges/faces 合并）的证据补进既有 `selection_helpers` 条目。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/amend_s209_b3_capabilities.py`
# 定位:   ★★ 裁决书要求「**扩**已有的 `solidworks_entities_on_body`，**不许开平行工具**」
#   ⇒ ★ 能力清单这一侧**同样不开平行条目**：把证据补进既有的 `selection_helpers` ✓
#   （★ 判据：`capabilities.yaml` 里那条已经列着 `solidworks_entities_on_body`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(r"D:\AI\SW\capabilities.yaml")

EVID = (
    "★★★ 真机（2026-10-06 · 规格 209 的 **B3 批** · idx **115 `edges`** + idx **145 `faces`**，"
    "★ 裁决书强制**合并成一条工具**）："
    "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b3_entities.py` ⇒ "
    "20×20×10 的拉伸盒：**FACE=6 · EDGE=12 · VERTEX=8**（★ 与几何相符），"
    "★★ **欧拉公式 `V − E + F = 2` 成立**（★ 本仓既有判据，**不需要任何新 API**）；"
    "★ 逐条几何**都读得到**：EDGE 的两个端点 + **自己算的边长** · FACE 的 `IFace2::GetArea()` · "
    "VERTEX 的 `IVertex::GetPoint()`；★ 负例（序号越界 / 非法 kind）**都大声报**"
    "（`EntitySelectionError`）✓ ★ 证据 `output/spec209-b3-entities.json`"
)

LIMITATION = (
    "★★ **本条目这一轮修掉的是一个「能枚举但交不出去」的缺口**（2026-10-06 · 规格 209 · B3-1）："
    "`entities_on_body` **返回 COM 对象** ⇒ ★ **过不了 MCP 的 JSON 边界** ⇒ 那条工具"
    "（`solidworks_entities_on_body`）**经工具层其实拿不到任何可用的东西**。"
    "★ 修法是**扩**而不是新开：**工具名不变**，指向改成 `entities_report`（只回 JSON）"
    "—— ★ 判据可核：`tests/test_tool_specs_batch14.py` 断言工具名唯一、且指向新函数 ✓"
)

EXTRA_LIMITATION = (
    "★★ **`IEdge` 上没有任何「长度」成员**（官方成员表逐条列过：`GetCurve` / `GetCurveParams` / "
    "`GetStartVertex` / `GetEndVertex` …）⇒ ★ 边长**只能由两个顶点自己算**。"
    "⚠ 这是 2026-10-06 **真机踩出来的**：按印象读 `IEdge.GetLength` ⇒ **12 条边全部抛异常**"
    "（★ 铁律 5：**名字缺席 = 官方没有这个成员**）。★ 已有静态断言不许它回来"
    "（`tests/test_tool_specs_batch14.py`）✓ "
    "⚠ **单位**：`IVertex::GetPoint` 的读数与文档长度单位一致（本机**毫米**）—— "
    "★ 判据是边长：厚 0.002 的板算出 `{0.002, 40, 60}`、厚 2 的算出 `{2.0, 40, 60}`"
    "（`output/spec209-hem-units.json`）✓"
)


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    hit = [c for c in caps if c.get("id") == "selection_helpers"]
    if len(hit) != 1:
        raise SystemExit("★ 找不到唯一的 selection_helpers（%d 条）⇒ 停手" % len(hit))
    e = hit[0]
    blob = json.dumps(e, ensure_ascii=False)
    if "spec209-b3-entities" in blob:
        print("★ 已补过 ⇒ 跳过")
    else:
        e.setdefault("evidence", []).append(EVID)
        e.setdefault("limitations", []).insert(0, LIMITATION)
        e["limitations"].append(EXTRA_LIMITATION)
        print("★ selection_helpers：+1 evidence · +2 limitations")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
