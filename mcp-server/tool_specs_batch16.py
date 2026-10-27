"""第十六批 MCP 工具声明：**草图几何关系 / 镜像特征** 2 个。

## 来源与筛选（2026-10-01 轮 209，Spec Kit `128`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
队列 A5 原写「`sw_part` 的安全子集（`add_sketch_relation` / `add_dimension`）」，
★ **实测后结论不同**：`add_dimension` **碰规则 3**（形参是裸坐标 `x, y`）⇒ **留批**。

### `sw_part` 的 14 个可注入孤立能力 —— 按**规则 2/3 精确分类**（不用关键词猜）
| 分类 | 个数 | 成员 |
|---|---|---|
| ★ **干净**（无坐标/长度/角度）| 3 | `add_sketch_relation` · **`insert_composite_curve`** · `mirror_feature` |
| ⚠ 碰**规则 3**（裸坐标）
| 6 | `add_dimension` · `hole_wizard` · `linear_pattern` · `sketch_arc` · `sketch_centerline` · `sketch_polygon` |
| ⚠ 碰**规则 2**（长度未带 `_mm`）| 5 | `circular_pattern` · `insert_dome` · `rib` · `shell` · `sketch_polygon` |
| ⚠ 碰**规则 2**（角度 `angle_rad`）| 2 | `circular_pattern` · `revolve_boss` |

★★ **而"干净"里的 `insert_composite_curve` 必须排除**（不是规则问题，是**它本来就坏**）：
```
已知事实 121 / 124：`InsertCompositeCurve` **一直返回 False**（前置条件已可达，成因未知）
⇒ ★ **挂它 = 把一个已知坏的入口摊给用户** ⇒ 本批**不挂**，并**不假装它会好**。
```

## 本批取的 2 个（签名照实取）
| 工具 | 函数 | 参数 | 备注 |
|---|---|---|---|
| ✅ | `sw_part.add_sketch_relation` | `(model, relation_type)
` | ★ `relation_type` 的合法值已按官方 Remarks 清单校正（2026-10-08 spec 222） |
| ✅ | `sw_part.mirror_feature` | `(model, feature_name, mirror_plane_name)` | 三个参数都是字符串 |

**`relation_type` 的合法值**（★ 引自 `IModelDoc2::SketchAddConstraints` 的官方 Remarks 清单，
`C:/swapi/types/IModelDoc2/SketchAddConstraints.md`，**不是猜的**）：
```
sgFIXED · sgHORIZONTAL · sgVERTICAL · sgCOLINEAR · sgPARALLEL · sgPERPENDICULAR
sgTANGENT · sgCONCENTRIC · sgSAMELENGTH · sgSYMMETRIC · sgATMIDDLE · sgCOINCIDENT
```
⚠ ★★ **2026-10-08 校正**：本文件此前把 `sgEQUAL` / `sgMIDPOINT` 当作合法值 —— 而官方
Remarks 清单里**没有**这两个串。⇒ 已改为官方名 **`sgSAMELENGTH`** / **`sgATMIDDLE`**；
旧名现在会被 `sw_part.add_sketch_relation` **拒绝并指出官方名**（不再静默失败）。

## 留批的 12 个（**逐条记明归属**，不留"以后再说"）
```
→ 规则 3（裸坐标）：add_dimension · hole_wizard · linear_pattern · sketch_arc ·
                    sketch_centerline · sketch_polygon   ⇒ 题队列 A8（写声明式选择包装层）
→ 规则 2（长度 _mm）：insert_dome · rib · shell ⇒ 名字改 `_mm` + `param_alias` 即可，**低风险**，
                    但**本批不夹带**（一批只做一类事，便于定位）
→ 规则 2（角度）：circular_pattern · revolve_boss ⇒ 题队列 A6（先定 `angle_rad → _deg` 的换算边界）
→ 本来就坏：insert_composite_curve ⇒ ★ **不挂**，等成因查明（事实 124）
```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch16.py
# 定位:   「孤立能力暴露」第十六批（Spec Kit `128`）—— 草图几何关系 + 镜像特征。
# 官方签名依据: 不适用（只做参数搬运）；`relation_type` 合法值引自目标函数 docstring
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH16"]

SPECS_BATCH16 = [
    ToolSpec(
        name="solidworks_add_sketch_relation",
        title="Add Sketch Relation",
        module="sw_part",
        function="add_sketch_relation",
        inject="model",
        evidence=(
            "Add a sketch geometric relation to the current selection."
        ),
        doc="Add a sketch geometric relation to the current selection.",
        params=[
            Param(
                "relation_type",
                str,
                description="Relation name. Valid values (each verified against the official "
                "IModelDoc2::SketchAddConstraints Remarks list, C:/swapi/types/"
                "IModelDoc2/SketchAddConstraints.md): "
                "sgFIXED, sgHORIZONTAL, sgVERTICAL, sgCOLINEAR, sgPARALLEL, "
                "sgPERPENDICULAR, sgTANGENT, sgCONCENTRIC, sgSAMELENGTH, sgSYMMETRIC, "
                "sgATMIDDLE, sgCOINCIDENT. "
                "The 'sg' prefix is optional and matching is case-insensitive. "
                "Legacy names sgEQUAL / sgMIDPOINT do NOT exist in the official list "
                "and are rejected with a pointer to sgSAMELENGTH / sgATMIDDLE.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_mirror_feature",
        title="Mirror Feature",
        module="sw_part",
        function="mirror_feature",
        inject="model",
        evidence=(
            "Mirror an existing feature about a plane."
        ),
        doc="Mirror an existing feature about a plane.",
        params=[
            Param("feature_name", str, description="Name of the feature to mirror."),
            Param(
                "mirror_plane_name",
                str,
                description="Name of the mirror plane (plane names follow the SolidWorks UI "
                "language, e.g. 「Front Plane」/「前视基准面」).",
            ),
        ],
    ),
]
