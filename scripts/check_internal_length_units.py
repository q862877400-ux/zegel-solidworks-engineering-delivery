"""★ 全量纲单位纪律门禁 —— **任何带单位的形参都必须让单位出现在名字里**。

## 业主指令（第 60 轮）

> 不只是米和毫米，包括角度、弧秒分，还有其他一些尺寸，反正你看着来吧，
> 我也不知道除了角度和距离之外还有什么别的尺寸。任何的尺寸你都全面地扫一遍，
> 看看有哪些尺寸。

## 量纲清单从哪来（不靠我猜）

① **官方枚举**（`C:\\swapi\\enums\\`）—— SolidWorks 自己的单位分类：
   · swLengthUnit_e：swMM / swMETER / swCM / swINCHES /…
   · `swAngleUnit_e`：`swDEGREES` / `swRADIANS` / `swDEG_MIN` / **`swDEG_MIN_SEC`**
   · `swNumberboxUnitType_e`：`Length` / `Angle` / **`Density`** / **`Force`** /
     **`Frequency`** / **`Gravity`** / **`Percent`** / **`Stress`** / **`Time`**
   · `swUnitsForce_e` / `swUnitsEnergyUnit_e` / `swUnitsPowerUnit_e` /
     `swUnitsTimeUnit_e` / `swUnitsMassPropMass_e` / `swUnitsMassPropVolume_e`
② **仿真/工程常见量**（SolidWorks Simulation 的载荷与材料参数就是这些）：
   力矩、压力、温度、速度、加速度、角速度、角加速度、刚度、阻尼、应变、
   热膨胀系数、热流密度、传热系数。

## 判据

形参名（去默认值）命中某量纲的**有界词表**，且**没有该量纲的后缀** ⇒ 违规。
后缀白名单按量纲分开（`_mm` 不能顶替 `_deg`、`_mpa` 不能顶替 `_n`）。

★ 棘轮：`docs/unit-naming-baseline.json` 只许降不许升（分总量纲与逐量纲两层）。

## 为什么不用「从描述推断量纲」

仓库试过（`tools/check_unit_suffix_reverse.py` 的第一版），实录误报：
`deg` 命中 `degenerate`、「度」命中**深**度 / **厚**度 / 粗糙**度**。
⇒ 本门禁只认**名字**与**有界词表**，确定性优先。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（门禁 · 全量纲单位命名）
# 文件:   scripts/check_internal_length_units.py
# 定位:   扫 scripts/ 与 tools/ 的函数形参，凡是**带量纲**的（长度/角度/时间/力/应力/…）
#          必须让单位出现在名字里。真因：本仓两套约定并存且形参都是裸名
#          （sw_part 收毫米、sw_assembly.add_component 收米）⇒ 调用方无从分辨，
#          实测把组件放到 30 米外。业主 2026-10-26：「从根本上解决」。
# 官方依据: C:\swapi\enums\swLengthUnit_e.md · swAngleUnit_e.md ·
#          swNumberboxUnitType_e.md · swUnitsForce_e.md · swUnitsEnergyUnit_e.md ·
#          swUnitsPowerUnit_e.md · swUnitsTimeUnit_e.md · swUnitsMassPropMass_e.md ·
#          swUnitsMassPropVolume_e.md
#          （量纲清单取自这些官方枚举，不靠猜）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

BASELINE = R / "docs" / "unit-naming-baseline.json"
EXEMPT = R / "docs" / "unit-naming-exempt.yaml"
SCAN_DIRS = ("scripts", "tools")

#: ★★ 全量纲表：`名 -> (词表, 后缀白名单, 说明)`
#:
#: ★ 词表是**有界**的，刻意不收 `size` / `value` / `count` / `rate` 这类语义词 ——
#:   收进来会天天误报，最后被人整条关掉（比不设更糟）。
QUANTITIES: dict = {
    "length": (
        {
            "x", "y", "z", "dx", "dy", "dz",
            "cx", "cy", "cz", "px", "py", "pz",
            "radius", "diameter", "distance", "gap", "offset",
            "thickness", "width", "height", "length", "depth",
            "clearance", "tolerance", "pitch", "spacing", "margin",
            "extent", "span", "stock", "allowance", "deflection",
        },
        ("_mm", "_m", "_um", "_nm", "_inch", "_mil", "_cm"),
        "长度（官方 swLengthUnit_e）",
    ),
    "angle": (
        {"angle", "rotation", "theta", "phi", "arc", "sweep", "twist",
         "tilt", "lean", "azimuth", "elevation", "draft"},
        ("_deg", "_rad", "_degmin", "_degminsec"),
        "角度（官方 swAngleUnit_e，含 DEG_MIN / DEG_MIN_SEC）",
    ),
    "area": (
        {"area", "surface_area", "cross_section", "section_area"},
        ("_mm2", "_m2", "_cm2"),
        "面积",
    ),
    "volume": (
        {"volume", "capacity"},
        ("_mm3", "_m3", "_cm3", "_l"),
        "体积（官方 swUnitsMassPropVolume_e）",
    ),
    "mass": (
        {"mass", "weight_mass"},
        ("_g", "_kg", "_mg", "_lb"),
        "质量（官方 swUnitsMassPropMass_e）",
    ),
    "density": (
        {"density"},
        ("_kg_m3", "_g_cm3"),
        "密度（官方 swNumberBox_Density）",
    ),
    "force": (
        {"force", "load_force", "reaction", "preload", "tension", "compression"},
        ("_n", "_kn", "_mn", "_kgf", "_lbf"),
        "力（官方 swUnitsForce_e）",
    ),
    "stress": (
        {"stress", "pressure", "yield_strength", "uts", "von_mises", "modulus"},
        ("_mpa", "_pa", "_kpa", "_gpa", "_psi"),
        "应力/压力/模量（官方 swNumberBox_Stress / Pressure）",
    ),
    "moment": (
        {"moment", "torque"},
        ("_nm", "_nmm", "_kgfm"),
        "力矩/扭矩",
    ),
    "temperature": (
        {"temperature", "temp"},
        ("_c", "_k", "_f"),
        "温度",
    ),
    "time": (
        {"time", "duration", "period", "interval", "timeout", "delay"},
        ("_s", "_ms", "_us", "_min", "_h"),
        "时间（官方 swUnitsTimeUnit_e）",
    ),
    "frequency": (
        {"frequency", "freq", "rpm"},
        ("_hz", "_khz", "_rpm"),
        "频率/转速（官方 swNumberBox_Frequency）",
    ),
    "energy": (
        {"energy", "heat"},
        ("_j", "_kj", "_kwh", "_btu", "_cal"),
        "能量（官方 swUnitsEnergyUnit_e）",
    ),
    "power": (
        {"power"},
        ("_w", "_kw", "_hp"),
        "功率（官方 swUnitsPowerUnit_e）",
    ),
    "velocity": (
        {"velocity", "speed", "feed_rate"},
        ("_mm_s", "_m_s", "_mm_min", "_m_min"),
        "线速度/进给",
    ),
    "acceleration": (
        {"acceleration", "accel"},
        ("_mm_s2", "_m_s2", "_g"),
        "线加速度（官方 swNumberBox_Gravity）",
    ),
    "angular_velocity": (
        {"angular_velocity", "omega"},
        ("_deg_s", "_rad_s", "_rpm"),
        "角速度",
    ),
    "angular_acceleration": (
        {"angular_acceleration", "alpha"},
        ("_deg_s2", "_rad_s2"),
        "角加速度",
    ),
    "stiffness": (
        {"stiffness", "spring_rate", "spring_stiffness", "damping"},
        ("_n_mm", "_n_m", "_nm_rad", "_ns_mm"),
        "刚度/阻尼",
    ),
    "percent": (
        {"percent", "ratio_pct", "pct"},
        ("_pct", "_percent"),
        "百分比（官方 swNumberBox_Percent）",
    ),
    "strain": (
        {"strain", "elongation"},
        ("_strain", "_ue"),
        "应变/伸长率",
    ),
}

#: ★ 兼容旧词表名（`test_unit_discipline_root_cause.py` 引用了它）
LEN_WORDS = QUANTITIES["length"][0]


#: ★ 选择器后缀：`force_type` 是「**选哪个**力类型」，不是「多少牛」。
#:   不收这些会让门禁把枚举参数当量值报 ⇒ 误报 ⇒ 门禁失去信任。
SELECTOR_SUFFIXES = (
    "_type", "_mode", "_kind", "_unit", "_option", "_flag",
    "_count", "_index", "_name", "_id", "_style", "_method",
    "_analysis", "_state", "_enum",
)


def _kind_of(name: str) -> tuple:
    """返回 `(量纲名, 词)`；不是带单位的量返回 `(None, "")`。"""
    low = name.lower().lstrip("_")
    if _has_suffix(low):
        return None, ""
    #: ★ 选择器不是量值（第一版把 `force_type` 报成违规 = 误报）
    if any(low.endswith(s) for s in SELECTOR_SUFFIXES):
        return None, ""
    head = low.split("_")[0]
    for kind, (words, _suf, _note) in QUANTITIES.items():
        if head in words or low in words:
            return kind, head
    return None, ""


def _has_suffix(name: str) -> bool:
    low = name.lower()
    for _kind, (_words, suffixes, _note) in QUANTITIES.items():
        if any(low.endswith(s) for s in suffixes):
            return True
    return False


def _suffix_ok(name: str, *, angle: bool = False) -> bool:
    """★ 兼容旧接口：这个名字是否带了（任一角度的 / 长度的）单位后缀。"""
    low = name.lower()
    if angle:
        return any(low.endswith(s) for s in QUANTITIES["angle"][1])
    return any(low.endswith(s) for s in QUANTITIES["length"][1])


def _is_len_name(name: str) -> bool:
    return _kind_of(name)[0] == "length"


def _is_angle_name(name: str) -> bool:
    return _kind_of(name)[0] == "angle"


def _load_exempt() -> dict:
    """★ 豁免表（`docs/unit-naming-exempt.yaml`）：`target: 理由`。
    ★ **没理由不算豁免** —— 空理由的条目会被忽略，不产生豁免效果。
    """
    if not EXEMPT.is_file():
        return {}
    try:
        import yaml

        data = yaml.safe_load(EXEMPT.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        return {}
    out: dict = {}
    for item in data.get("exemptions") or ():
        key = str(item.get("target") or "")
        why = str(item.get("reason") or "").strip()
        if key and why:
            out[key] = why
    return out


def scan() -> tuple:
    """全仓扫描。返回 `(violations, excused, files)`。"""
    exempt = _load_exempt()
    violations: list = []
    excused: list = []
    files = 0

    for d in SCAN_DIRS:
        for p in sorted((R / d).rglob("*.py")):
            #: ★ 2026-11-04：`scripts/cad_workbench/` 是从已删除的桌面工作台迁过来的库
            #:   （`cad_studio.py` / `headless_cad_writer.py` / `headless_occt_service.py`
            #:   与 12 个测试仍在用），内容未重写 ⇒ 与 `check_repo_uniformity.EXCLUDE_HINT`
            #:   **同一口径**排除，避免把历史命名欠账算进棘轮上界。欠账记在那边注释里。
            if "scripts/cad_workbench" in p.as_posix():
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            files += 1
            rel = p.relative_to(R).as_posix()
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for arg in list(node.args.args) + list(node.args.kwonlyargs):
                    nm = arg.arg
                    if nm in ("self", "cls"):
                        continue
                    kind, word = _kind_of(nm)
                    if not kind:
                        continue
                    key = "%s::%s::%s" % (rel, node.name, nm)
                    if key in exempt:
                        excused.append({"target": key, "kind": kind})
                        continue
                    violations.append(
                        {
                            "target": key,
                            "file": rel,
                            "function": node.name,
                            "param": nm,
                            "line": arg.lineno,
                            "kind": kind,
                            "word": word,
                        }
                    )
    return violations, excused, files


def inventory(violations: list) -> None:
    """★ 打印**量纲清单**：各量纲多少处、集中在哪些文件。

    ★ 这就是业主说的「全面扫一遍」的产出 —— 让人看见到底有多少种量纲。
    """
    by_kind: dict = {}
    for v in violations:
        by_kind.setdefault(v["kind"], []).append(v)
    print("\n── 量纲清单（裸名违规，按量纲分组）──")
    for kind in sorted(by_kind, key=lambda k: -len(by_kind[k])):
        note = QUANTITIES[kind][2]
        files = len({v["file"] for v in by_kind[kind]})
        print(
            "  %-20s %3d 处 / %2d 个文件   %s"
            % (kind, len(by_kind[kind]), files, note)
        )
    print("\n── 覆盖到的量纲种类 ──")
    kinds = sorted(QUANTITIES)
    print("  " + " · ".join(kinds))


def main() -> int:
    violations, excused, files = scan()
    n = len(violations)

    base = {}
    if BASELINE.is_file():
        try:
            base = json.loads(BASELINE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            base = {}
    ceiling = int(base.get("ceiling", n))

    print("[扫描] %d 个文件 · 违规 %d 处 · 豁免 %d 处（上界 %d）"
          % (files, n, len(excused), ceiling))

    by_file: dict = {}
    for v in violations:
        by_file.setdefault(v["file"], []).append(v)
    for rel in sorted(by_file, key=lambda k: -len(by_file[k]))[:8]:
        names = ", ".join(
            "%s(%s)" % (v["param"], v["function"]) for v in by_file[rel][:4]
        )
        print("   %-46s %d 处：%s" % (rel, len(by_file[rel]), names))

    if "--inventory" in sys.argv:
        inventory(violations)

    if n > ceiling:
        print("★ [FAIL] 裸量纲形参 %d 处 > 上界 %d —— 一个都不许新增" % (n, ceiling))
        for v in violations[:12]:
            print("   %s:%s  %s(%s)  [%s]" % (v["file"], v["line"], v["function"],
                                              v["param"], v["kind"]))
        return 1

    print("★ [PASS] 裸量纲形参 %d 处 ≤ 上界 %d（棘轮：只许降）" % (n, ceiling))
    if not BASELINE.is_file():
        BASELINE.write_text(
            json.dumps(
                {"ceiling": n, "note": "初始基线（第 60 轮，全量纲版）"},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print("   已写初始基线：%s" % BASELINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
