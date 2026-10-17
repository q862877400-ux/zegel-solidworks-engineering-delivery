"""★ 规格 209 · B4-3（idx 181 intersect）：把 `part_intersect` 能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b4c_capabilities.py`
# 定位:   ★ 追加 **1 条**能力 `part_intersect`（两步相交 + 布尔 SafeArray 包装已验）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(Path(__file__).resolve().parents[1] / "capabilities.yaml")

ENTRY = {
    "id": "part_intersect",
    "label": "相交特征（`IFeatureManager::PreIntersect2` → `PostIntersect`，**官方两步**）—— "
             "★ 真机建成 `相交1` · ★ 布尔 SafeArray 包装已验",
    "level": "verified",
    "verified_versions": ["2026"],
    "backends": ["solidworks-com-pywin32"],
    "dependencies": ["solidworks"],
    "evidence": [
        "★★★ 真机（2026-10-06 · 规格 209 的 **B4-3** · idx **181**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b4_intersect.py` ⇒ "
        "60×40×20 的板 + 基准面，按**名字 + 类型**选（`SOLIDBODY:凸台-拉伸1,PLANE:前视基准面`）⇒ "
        "**四种组合**（`region_type` ∈ {`intersecting`, `intersecting_and_internal`} × "
        "`exclude` ∈ {空, `0`}）："
        "① 不排除 ⇒ `PreIntersect2` 回 **1 个体**、`PostIntersect` 建出 **`相交1`**、"
        "`IIntersectFeatureData::GetIntersectionsCount()` 回 **1**（★ 两种 region_type 都成立）；"
        "② ★★ **排除唯一的体** ⇒ `PostIntersect` **回 `None`**、特征**没建出来**"
        "（树增量 0）✓ ★ 证据 `output/spec209-intersect.json`",
        "★★ **裁决书点名「唯一要实测」的那件事已验**：`PostIntersect` 的第 1 参是 "
        "**`System.object`（布尔 SafeArray）** —— ★ 本仓包 **`VARIANT(VT_ARRAY | VT_BOOL)`**，"
        "★★ 而**真机是「双向」证实的**：不排除 ⇒ 建出特征；**把唯一的体标成排除** ⇒ "
        "特征**建不出来** ⇒ ★★ **说明那个 `True` 真的被 SW 读走了**（★ 不是「参数被忽略但没报错」）✓",
        "★ 官方依据逐页读过：`C:\\swapi\\types\\IFeatureManager\\PreIntersect2.md`"
        "（`System.object PreIntersect2(System.bool CapPlanar, System.int RegionType)`；"
        "`## Parameters` 逐字给出 **RegionType 三值**；`## Remarks` 逐字要求**先选中**相交的"
        "曲面/实体/基准面）· `IFeatureManager\\PostIntersect.md`"
        "（`Feature PostIntersect(System.object, System.bool Merge, System.bool Consume)`；"
        "`IntersectionsToExclude` 逐字是「**Array of booleans**」）· "
        "`IIntersectFeatureData\\{GetIntersectionsCount,CapPlanar,Merge,Consume}.md` · "
        "★★ `examples\\Create_Intersect_Feature_Example_VB.md`（**调用序**：名字+类型选、都 **mark 0**、"
        "清选区、拼**与体数等长**的布尔数组、`PostIntersect(arr, True, False)`）",
    ],
    "limitations": [
        "★ **数组实参必须包 `VARIANT`** —— ★ 本仓既有教训（`scripts/sketch_relations.py` 轮 183 实测）："
        "「裸 `list`/`tuple` 会**静默返回 `None`**」⇒ ★ 本模块的布尔数组一律包 "
        "`VARIANT(VT_ARRAY | VT_BOOL)`，★ 并加静态断言钉住 ✓",
        "★ 判据用 **`IIntersectFeatureData::GetIntersectionsCount()`**（**零参回 int**）—— "
        "⚠ **不用** `GetIntersections(out Excluded)`：它有 **out 参**，而本仓已知**pywin32 下 out 参"
        "不保证回写**（事实同族）⇒ ★ 需要「哪个体被排除了」时应改用别的方式取，"
        "★ **不要**拿 out 参的读数当判据 ✓",
        "⚠ **未验**：★ 只验了**一个实体 + 一个基准面**这种两对象前置；"
        "★ **两个实体相交**（多体布尔）· **曲面**相交 · `cap_planar=True` 的封盖 · "
        "`merge=False`（不合并）· `consume=True`（移除输入曲面）**均未验** ✓",
        "⚠ **前置语义**：官方 `## Remarks` 只说「**先选中**相交的曲面/实体/基准面」，"
        "★ **没说什么组合合法** ⇒ ★ 本模块**原样透传**、不猜；"
        "★ 选不中就**在进 COM 前报错**（选区计数 0）✓",
        "★ `exclude` **把全部体都排除**时 ⇒ `PostIntersect` 回 `None`、特征不建"
        "（★ 真机实测，属**应然**：没有体可以组成相交区域）—— ★ 本模块如实判 `ok=False` ✓",
    ],
    "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序**立）："
                       "`C:\\swapi\\types\\IFeatureManager\\{PreIntersect2,PostIntersect}.md` · "
                       "`C:\\swapi\\types\\IIntersectFeatureData\\*.md` · "
                       "官方示例 `Create_Intersect_Feature_Example_VB.md` —— ★ **逐页读过** ✓ "
                       "★ 落点 `scripts/sw_boolean_ops.py`（**新建**；★ 本仓既有零件特征模块里"
                       "**没有多体/布尔这一族** —— 裁决书 §九 指定的落点就是它，★ 仍在 `scripts/` 白名单内）· "
                       "★ **不来自任何外部项目** ✓",
    "source": "original",
    "allowed_modes": ["interactive", "reviewed", "unattended"],
    "mcp_tools": ["solidworks_part_intersect"],
}


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == ENTRY["id"] for c in caps):
        print("★ 已存在 ⇒ 跳过")
    else:
        caps.append(ENTRY)
        print("★ 追加 part_intersect")
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
