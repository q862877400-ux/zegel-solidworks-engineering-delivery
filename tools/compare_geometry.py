"""★ **几何等价判据**（拓扑 + |ΔV| + |ΔA|）—— 2026-10-01 · 轮 321。

## 为什么写它
```
★ 本仓库原先进 `specs/*` 的真机判据是**包围盒相等**（例：`specs/136` 的拉伸族断言
   `bbox == [40, 20, 10]`）⇒ ★★ **包围盒相同 ≠ 形状相同** ——
   倒角、挖槽、放样错接都能在包围盒不变的情况下做错。
★ 而**社区已有更强的判据**（★ 来源见下）：**拓扑全等 且 |ΔV| ≤ 1% 且 |ΔA| ≤ 1%**。
⇒ ★ 本模块把那**判据**（★ 不是代码 —— 来源是 AGPL，铁律 6 只读思想）搬进来，
   ★ 与既有的**特征类型名**判据（事实 242：`Blend` / `Sweep` / `ICE` / `Extrusion` /
   `CirPattern` / `MirrorPattern`）**互补**：
     · 类型名 ⇒ 判「**特征建成了没有**」（★ 只依赖 API 对不对）
     · 本模块 ⇒ 判「**几何对不对**」（★ 只依赖几何算得准不准）
```

## ★ 三条判据（每条都能独立说不）
| 判据 | 怎么算 | 为什么它比包围盒强 |
|---|---|---|
| **拓扑全等** | 面数 + 边数 + 顶点数（★ 三数全等） | 挖一个槽 ⇒ 面数变；放样错接 ⇒ 边数变 |
| **\\|ΔV\\| ≤ 1%** | 两文档各自的质量属性 `Volume` | 尺寸错 1% 以上就抓到 |
| **\\|ΔA\\| ≤ 1%** | 两文档各自的 `SurfaceArea` | 形状对而壁厚错的也能抓到 |

## ★ 来源（铁律 1）
```
仓库:   `Bennyco86/q3ds-solidworks-mcp`（= `eyfel/mcp-server-solidworks` 即 **SolidPilot** 的 fork）
许可:   **AGPL-3.0** ⇒ ★★ **只读思想，不抄代码、不抄文本**（铁律 6）
依据:   其 README 自述 `compare_parts` —— 「对两个零件做客观 diff（拓扑 / 体积 / 表面积 / 重心），
        `verified` 的条件是**拓扑完全相同 且 |ΔV| ≤ 1% 且 |ΔA| ≤ 1%**；
        且**每个零件都在全新文档里重建**，再与原件比」。
本机调研: `D:\\AI\\SW\\docs\\research-community-sw-mcp-2026-10-02.md` §二①
★ 我们搬的是**判据与阈值**，实现是本仓库自己写的（★ 用 `IModelDocExtension.CreateMassProperty`）。
```

## ★★ 用法
```python
from compare_geometry import collect_geometry, compare_geometry
a = collect_geometry(doc_a)          # {'faces':…, 'edges':…, 'vertices':…, 'volume_mm3':…, 'area_mm2':…}
b = collect_geometry(doc_b)
rep = compare_geometry(a, b)         # {'ok': bool, 'reasons': [...], 'deltas': {...}}
```
⇒ ★ 判据：**`ok` 为真**才允许在文档里写「几何已验证」。
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   `Bennyco86/q3ds-solidworks-mcp`（= `eyfel/mcp-server-solidworks` 即 **SolidPil
# ot** 的 fork）
# ★ 该来源的许可是 **AGPL-3.0** ⇒ ★ **按铁律 6「只读思想」**：本文件**不抄**其代码、**不
# 抄**其文本，
#         ★ 只搬**判据与阈值**（拓扑全等 + |ΔV| ≤ 1% + |ΔA| ≤ 1% 这个公开的判据口径）。
# 文件:   tools/compare_geometry.py —— 本文件（判据实现；★ **代码是本仓库自己写的**）
# 定位:   真机证据的**几何等价判据**（★ 与「特征类型名」判据互补，事实 242）。
# 官方签名依据: `C:\swapi\types\IMassProperty\`（`Volume` / `SurfaceArea`）·
# `C:\swapi\types\IModelDocExtension\CreateMassProperty.md` · `C:\swapi\types\IBody2\Get
# Faces.md`
# 许可:   本文件 MIT（本仓库自身）—— ★ **本仓库全部代码均为 MIT**，无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

#: ★★ 2026-10-03（轮 470）**修一个真 bug**：`_ROOT_S` 原定义在下面，而本行就用了它
#:   ⇒ `NameError` ⇒ **`import compare_geometry` 直接失败** ⇒ 该测试文件收集期就报错。
#:   ★ 它是**事实 375 记的那族**（用了却没定义 / 定义在使用之后）——
#:   合并那轮修了 7 个同类，**漏了这一个**。
_ROOT_S = str(Path(__file__).resolve().parents[1])

sys.path[:0] = [str(Path(__file__).resolve().parent), r"" + _ROOT_S + r"\scripts"]

from sw_connect import get_com_member  # noqa: E402

#: ★ 相对容差（★ 来自来源 README 的 1% —— 那是一个**量级**，不是我们拍的）

REL_TOL = 0.01


def collect_geometry(model) -> dict:
    """★ 读一个文档的**几何指纹**（面/边/顶点计数 + 体积 + 表面积）。

    ★ 单位：★ `Volume` 回 **m³** ⇒ 乘 1e9 得 mm³；`SurfaceArea` 回 **m²** ⇒ 乘 1e6 得 mm²。
      ★ 三源互证见 `scripts/sw_mass_property.py` 的既有实现（★ 本模块只读，不重复换算）。
    """
    out = {
        "faces": None,
        "edges": None,
        "vertices": None,
        "volume_mm3": None,
        "area_mm2": None,
    }
    nf = ne = nv = 0
    try:
        for body in get_com_member(model, "GetBodies2", 0, False) or []:
            for f in get_com_member(body, "GetFaces") or []:
                nf += 1
                for loop in get_com_member(f, "GetLoops") or []:
                    for e in get_com_member(loop, "GetEdges") or []:
                        ne += 1
                    for v in get_com_member(loop, "GetVertices") or []:
                        nv += 1
        out.update({"faces": nf, "edges": ne, "vertices": nv})
    except Exception as exc:  # noqa: BLE001
        out["count_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    try:
        mp = get_com_member(get_com_member(model, "Extension"), "CreateMassProperty")
        #: ★★★ 2026-10-01（轮 321）**不要乘**：真机实测一块 40×20×10 mm 的板 ⇒
        #:   `Volume` 回 **8000**（★ 就是 **mm³**）· `SurfaceArea` 回 **2800**（mm²）
        #:   —— ★ 而我初版乘了 1e9 / 1e6（★ 以为它回 SI）⇒ 得到 8e12 / 2.8e9。
        #: ★ 即：**本机的 `IMassProperty` 按文档默认单位（mm）回值**（★ 与事实里「SW 默
        #: 认单位 = mm」一致）。
        #: ★ 而**相对判据不受刻度影响** —— ★ 所以当时 ΔV=2% 仍然抓对了（★ 那是相对判据的
        #: 鲁棒之处）。
        out["volume_mm3"] = round(float(get_com_member(mp, "Volume")), 6)
        out["area_mm2"] = round(float(get_com_member(mp, "SurfaceArea")), 6)
    except Exception as exc:  # noqa: BLE001
        out["mass_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return out


def compare_geometry(a: dict, b: dict, rel_tol: float = REL_TOL) -> dict:
    """★ **几何等价判据**：★ 拓扑全等（面/边/顶点三数全等）**且** |ΔV| ≤ tol **且** |ΔA| ≤ tol。

    ★ 回 `{"ok", "reasons", "deltas"}` —— ★ `reasons` **逐条给出不通过的理由**（★ 便于写进证据）。
    ★ 缺项（`None`）⇒ ★ **判不通过**（★ 而不是"跳过" —— ★ 读不到就不算验过）。
    """
    reasons, deltas = [], {}
    for k in ("faces", "edges", "vertices"):
        va, vb = a.get(k), b.get(k)
        if va is None or vb is None:
            reasons.append("拓扑计数读不到（%s: a=%r b=%r）" % (k, va, vb))
        elif va != vb:
            reasons.append("拓扑不同（%s: %d vs %d）" % (k, va, vb))
    for k in ("volume_mm3", "area_mm2"):
        va, vb = a.get(k), b.get(k)
        if va is None or vb is None:
            reasons.append("质量属性读不到（%s: a=%r b=%r）" % (k, va, vb))
            continue
        base = abs(va) if abs(va) > 1e-12 else 1.0
        d = abs(vb - va) / base
        deltas[k] = round(d, 6)
        if d > rel_tol:
            reasons.append(
                "%s 偏离 %.4f%% > 容差 %.2f%%" % (k, d * 100.0, rel_tol * 100.0)
            )
    return {
        "ok": not reasons,
        "reasons": reasons,
        "deltas": deltas,
        "rel_tol": rel_tol,
        "a": a,
        "b": b,
        "★": "来源 AGPL（SolidPilot/q3ds 的 compare_parts README）⇒ **只搬判据与阈值**；"
        "★ 与「特征类型名」判据互补（事实 242）",
    }


#: ★ **绝对 mm 容差**（★ 与上面的**相对**判据互补，★ **不是替代**）——
#: ★ 判据来源：★ `Cai-aa/CAD-Agent-Hub`（**MIT**）的
#:   `MCP/Solidworks/src/solidworks_mcp/native_features.py`（★ 本机已克隆，★ 逐行读过）：
#:     · `L642` ⇒ `tolerance = float(selector.get("tolerance_mm", **0.05**)) * MM`
#: · `L647` ⇒ `radius_tolerance = float(selector.get("radius_tolerance_mm", **0.1**)) *
#: MM`
#:     · `L655` ⇒ `axial`：`abs(dx) <= tol and abs(dy) <= tol and abs(dz) > tol`
#:     · `L657` ⇒ `planar`：`abs(dz) <= tol`
#:     · `L662` ⇒ 半径逐个判：`any(abs(v - radius) > radius_tolerance for v in radii)`
#:     · `L665` ⇒ 两端点同层：`abs(start[2]-level) <= tol and abs(end[2]-level) <= tol`
#:     · `L238` ⇒ 回读校验用 **1e-5**（★ 那个更严，★ 是给"读回来的值对不对"用的）
ABS_TOL_MM = 0.05  # 位置容差（native_features.py:642 的默认）
RADIUS_TOL_MM = 0.1  # 半径容差（:647 的默认）
READBACK_TOL_MM = 1e-5  # 回读校验（:238）


def check_axis_alignment(
    delta_mm, orientation: str = "axial", tol_mm: float = ABS_TOL_MM
) -> dict:
    """★ **方位/定位判据（绝对 mm · 逐轴 · 带方位语义）**。

    ★ 两类语义（★ 照 `native_features.py:655/657`）：
      · **`axial`**（★ "这根轴是轴对齐的"）⇒ 横向两轴 `|dx| ≤ tol` **且** `|dy| ≤ tol`
        **且** 轴向 `|dz| > tol` —— ★★ **注意最后一条是"大于"**：★ 轴向**必须**长出一截，
        ★ 否则它就不是"轴"，★ 而是一条横躺的边。
      · **`planar`**（★ "这个面是平的/法向对齐的"）⇒ 轴向 `|dz| ≤ tol`。
    ★★ **为什么相对判据替代不了它**：★ 整体平移时**所有相对量都不变** ⇒
      ★ 相对判据对"位置错了"完全瞎；★ 而本判据只看绝对差值。
    """
    try:
        dx, dy, dz = (float(v) for v in delta_mm)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "reasons": ["delta_mm 要是三个数，实得 %r" % (delta_mm,)],
            "deltas": {},
        }
    if orientation == "axial":
        ok = abs(dx) <= tol_mm and abs(dy) <= tol_mm and abs(dz) > tol_mm
        want = "|dx|<=tol 且 |dy|<=tol 且 **|dz|>tol**"
    elif orientation == "planar":
        ok = abs(dz) <= tol_mm
        want = "|dz|<=tol"
    else:
        return {
            "ok": False,
            "reasons": ["orientation 只能是 axial 或 planar，实得 %r" % (orientation,)],
            "deltas": {},
        }
    reasons = (
        []
        if ok
        else [
            "方位不符（%s）：期望 %s，实得 dx=%.6f dy=%.6f dz=%.6f，tol=%.6f"
            % (orientation, want, dx, dy, dz, tol_mm)
        ]
    )
    return {
        "ok": ok,
        "reasons": reasons,
        "orientation": orientation,
        "tol_mm": tol_mm,
        "deltas": {"dx": round(dx, 6), "dy": round(dy, 6), "dz": round(dz, 6)},
        "★": "★ 绝对 mm · 逐轴 · 带方位语义（判据来源 native_features.py:655/657，MIT）",
    }


def check_radii(
    radii_mm, expected_radius_mm: float, tol_mm: float = RADIUS_TOL_MM
) -> dict:
    """★ **半径逐值判据**（★ 照 `native_features.py:662`）—— ★ 一个不等就不过。"""
    try:
        vals = [float(r) for r in radii_mm]
    except (TypeError, ValueError):
        return {
            "ok": False,
            "reasons": ["radii_mm 要是数列，实得 %r" % (radii_mm,)],
            "max_dev": None,
        }
    if not vals:
        return {
            "ok": False,
            "reasons": ["radii_mm 是空的 —— ★ 读不到就不算验过"],
            "max_dev": None,
        }
    devs = [abs(v - float(expected_radius_mm)) for v in vals]
    worst = max(devs)
    ok = worst <= tol_mm
    return {
        "ok": ok,
        "reasons": []
        if ok
        else [
            "有 %d/%d 个半径超出容差：最大偏离 %.6f mm > %.6f mm"
            % (sum(1 for d in devs if d > tol_mm), len(devs), worst, tol_mm)
        ],
        "max_dev": round(worst, 6),
        "tol_mm": tol_mm,
        "count": len(vals),
        "★": "★ 绝对 mm · 逐值（判据来源 native_features.py:662，MIT）",
    }


def check_same_level(z_pairs_mm, level_mm: float, tol_mm: float = ABS_TOL_MM) -> dict:
    """★ **两端点是否同层**（★ 照 `native_features.py:665`）—— 两个端点都要落在 level 上。"""
    try:
        pairs = [(float(a), float(b)) for a, b in z_pairs_mm]
    except (TypeError, ValueError):
        return {
            "ok": False,
            "reasons": ["z_pairs_mm 要是二元组列，实得 %r" % (z_pairs_mm,)],
            "max_dev": None,
        }
    if not pairs:
        return {"ok": False, "reasons": ["z_pairs_mm 是空的"], "max_dev": None}
    devs = [abs(a - float(level_mm)) for a, _ in pairs] + [
        abs(b - float(level_mm)) for _, b in pairs
    ]
    worst = max(devs)
    ok = worst <= tol_mm
    return {
        "ok": ok,
        "reasons": []
        if ok
        else [
            "有端点不在 level=%.6f 上：最大偏离 %.6f mm > %.6f mm"
            % (level_mm, worst, tol_mm)
        ],
        "max_dev": round(worst, 6),
        "tol_mm": tol_mm,
        "★": "★ 绝对 mm · 逐端点（判据来源 native_features.py:665，MIT）",
    }


def main() -> int:
    """★ 自证：★ 判据必须能对**构造出来的差异**说不（★ 事实 62：负例是唯一的证明）。"""
    same = {
        "faces": 6,
        "edges": 12,
        "vertices": 8,
        "volume_mm3": 8000.0,
        "area_mm2": 2400.0,
    }
    ok = compare_geometry(same, dict(same))
    print(
        "  \u540c\u4e00\u4efd\u51e0\u4f55 \u21d2 ok=%s\uff08\u2605 \u5e94\u4e3a True\uff09"
        % ok["ok"]
    )
    cases = {
        "\u4f53\u79ef\u5dee 1.5%": dict(same, volume_mm3=8000.0 * 1.015),
        "\u9762\u6570\u5dee 1": dict(same, faces=7),
        "\u8fb9\u6570\u5dee 2": dict(same, edges=14),
        "\u9762\u79ef\u5dee 2%": dict(same, area_mm2=2400.0 * 1.02),
        "\u4f53\u79ef\u8bfb\u4e0d\u5230": dict(same, volume_mm3=None),
    }
    bad = 0
    for lab, b in cases.items():
        r = compare_geometry(same, b)
        verdict = "\u2713 \u62d2\u4e86" if not r["ok"] else "\u2717 **\u6f0f\u4e86**"
        if r["ok"]:
            bad += 1
        print(
            "  %-16s \u21d2 ok=%-5s %s  %s"
            % (lab, r["ok"], verdict, (r["reasons"] or [""])[0][:52])
        )
    #: \u2605 \u5bb9\u5dee\u8fb9\u754c\uff1a\u521a\u597d 1% \u8be5\u8fc7\u3001\u521a\u8d
    #: 85\u4e00\u70b9\u8be5\u62d2
    edge_ok = compare_geometry(same, dict(same, volume_mm3=8000.0 * 1.01))["ok"]
    edge_bad = compare_geometry(same, dict(same, volume_mm3=8000.0 * 1.011))["ok"]
    print(
        "  容差边界: 1.0%%⇒%s（★ 应 True）· 1.1%%⇒%s（★ 应 False）"
        % (edge_ok, edge_bad)
    )
    #: ★★★ 2026-10-01（轮 326）**新增：绝对 mm 判据的自证** —— ★ 与上面的**相对**判据互
    #: 补。
    #: ★ 每个用例都是 `(名字, 判据结果, 期望 ok)`；★ **期望 False 的就是负例**（事实 62
    #: ）。
    print()
    print("  ── 绝对 mm · 逐轴 · 方位语义（★ 与相对判据互补）──")
    abs_cases = [
        (
            "axial 对齐（dx=dy=0 · dz=20）",
            check_axis_alignment((0.0, 0.0, 20.0), "axial"),
            True,
        ),
        (
            "axial 而 dz=0（★ 横躺 ⇒ 该拒）",
            check_axis_alignment((0.0, 0.0, 0.0), "axial"),
            False,
        ),
        (
            "axial 而 dx=0.06（★ 超容差）",
            check_axis_alignment((0.06, 0.0, 20.0), "axial"),
            False,
        ),
        (
            "planar 对齐（dz=0.01）",
            check_axis_alignment((5.0, 5.0, 0.01), "planar"),
            True,
        ),
        (
            "planar 而 dz=0.2（★ 该拒）",
            check_axis_alignment((5.0, 5.0, 0.2), "planar"),
            False,
        ),
        ("半径全对（5.0×3）", check_radii([5.0, 5.0, 5.0], 5.0), True),
        ("半径一个差 0.15（★ 该拒）", check_radii([5.0, 5.15, 5.0], 5.0), False),
        ("半径空列（★ 读不到不算验过）", check_radii([], 5.0), False),
        (
            "同层（都在 z=10）",
            check_same_level([(10.0, 10.0), (10.0, 10.0)], 10.0),
            True,
        ),
        ("不同层（★ 该拒）", check_same_level([(10.0, 10.2)], 10.0), False),
    ]
    abs_bad = 0
    for lab, r, want in abs_cases:
        if r["ok"] != want:
            abs_bad += 1
        print(
            "  %-34s ⇒ ok=%-5s %s"
            % (lab, r["ok"], "✓" if r["ok"] == want else "✗ **不符期望**")
        )
    print()
    ok_all = bad == 0 and edge_ok and not edge_bad and abs_bad == 0
    print(
        "  \u7ed3\u8bba: %s\uff08\u2605 \u76f8\u5bf9\u5224\u636e\u8d1f\u4f8b %d/%d\u3001\u8fb9\u754c %s\u3001"
        "\u7edd\u5bf9\u5224\u636e %d/%d\uff09"
        % (
            "PASS" if ok_all else "FAIL",
            len(cases) - bad,
            len(cases),
            "OK" if (edge_ok and not edge_bad) else "**\u4e0d\u5bf9**",
            len(abs_cases) - abs_bad,
            len(abs_cases),
        )
    )
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
