"""★ EC08 工程图与多工艺 —— 标注回读 / 悬空检测 / 钣金展开 / 焊件切割清单 / 曲面连续性。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC08**（★ 四个子域逐字）
#         `specs/310-ec08-drawing-and-processes/spec.md`
# 定位:   ★ **EC08** 的实现（★ 四个子域的**验收方法** —— ★ 能力都已在工具面）。
#         ★★★ 计划 §5 EC08 验收逐字：「★ 尺寸值、基准、公差、**模型配置版本**都能**回读比对**；
#           ★ **悬空标注检测**；★ 版面/遮挡/线型与可读性另设检查。
#           ★ **制图标准符合不代表整机安全合规**」
# 官方依据: 不适用（本仓的制图与工艺层 —— ★ **不调 SolidWorks API**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 真机部分见 `acceptance.md`）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "NOT_A_SAFETY_COMPLIANCE_STATEMENT",
    "AnnotationKind",
    "Annotation",
    "DanglingReport",
    "DrawingEvidence",
    "SheetMetalSpec",
    "unfold_consistency",
    "bend_interference",
    "WeldmentCutList",
    "cut_list_totals",
    "SurfaceContinuity",
    "surface_is_not_eyeballed",
]


#: ★★★ **免责声明**（★ 逐字承验收：★「★ **制图标准符合不代表整机安全合规**」）
#:   ★★ 每个工程图交付物**必须带**它 —— ★ 不是可选
NOT_A_SAFETY_COMPLIANCE_STATEMENT = (
    "★ 制图标准符合**不代表**整机安全合规（★ 安全合规由 EC11 按设备类别判）"
)


class AnnotationKind:
    """★ 标注种类（★ 逐字承 EC08A：★「★ **功能尺寸/基准/配合**、**公差**、**材料**、
    ★ **技术要求**、**BOM** 和**版本**」）。"""

    DIMENSION = "dimension"  #: ★ 尺寸
    DATUM = "datum"  #: ★ 基准
    FIT = "fit"  #: ★ 配合
    TOLERANCE = "tolerance"  #: ★ 公差
    MATERIAL = "material"  #: ★ 材料
    TECH_REQUIREMENT = "tech_requirement"  #: ★ 技术要求
    BOM = "bom"  #: ★ BOM
    VERSION = "version"  #: ★ 版本

    ALL = (DIMENSION, DATUM, FIT, TOLERANCE, MATERIAL, TECH_REQUIREMENT, BOM, VERSION)


@dataclass
class Annotation:
    """★★ **一个标注**（★ 带**它标的几何** —— ★ 悬空检测靠它）。"""

    kind: str
    text: str
    #: ★★ **它指向的几何**（★ 空 ⇒ ★ **悬空**）
    target: str = ""
    value: float | None = None
    unit: str = ""

    def is_dangling(self) -> bool:
        """★★★ **是不是悬空**（★ 逐字承验收：★「★ **悬空标注检测**」）。

        ★★ 判据：★ **没有 `target`** ⇒ ★ 悬空（★ 它没指回任何几何）。
        """
        return not str(self.target).strip()


@dataclass
class DanglingReport:
    """★★ **悬空标注报告**。"""

    annotations: list = field(default_factory=list)

    def dangling(self) -> list:
        return [a for a in self.annotations if a.is_dangling()]

    def verdict(self) -> dict:
        """★★ **判定**（★ 有悬空 ⇒ 不通过 —— ★ 且**逐条具名**）。"""
        bad = self.dangling()
        return {
            "ok": not bad,
            "count": len(bad),
            "dangling": [{"kind": a.kind, "text": a.text} for a in bad],
            "reason": (
                "★ %d 条标注都有指向" % len(self.annotations)
                if not bad
                else "★★ %d 条标注**悬空**（★ 没指回几何）" % len(bad)
            ),
        }


@dataclass
class DrawingEvidence:
    """★★★★ **工程图证据**（★ 逐字承验收：★「★ 尺寸值、基准、公差、**模型配置版本**
    都能**回读比对**」）。

    ★★★ **「回读比对」的意思**：★ 每项**都要有**：★ ① **标称值** ② **回读值**
      ⇒ ★ **两者必须能比**（★ 不是只写一个）。
    """

    items: list = field(default_factory=list)  #: `[{kind, nominal, readback, tol}]`
    model_config: str = ""  #: ★★ **模型配置版本**
    model_revision: str = ""  #: ★★ **模型版本**

    def add(self, kind: str, *, nominal: Any, readback: Any, tol: float = 0.0) -> None:
        self.items.append(
            {"kind": kind, "nominal": nominal, "readback": readback, "tol": tol}
        )

    def verdict(self) -> dict:
        """★★★ **判定**（★ 三类都要：★ 项齐 · ★ 回读齐 · ★ **版本已绑**）。"""
        missing_kinds = [
            k
            for k in (
                AnnotationKind.DIMENSION,
                AnnotationKind.DATUM,
                AnnotationKind.TOLERANCE,
            )
            if not any(i["kind"] == k for i in self.items)
        ]
        no_readback = [i["kind"] for i in self.items if i.get("readback") is None]
        mismatches = []
        for i in self.items:
            n, r = i.get("nominal"), i.get("readback")
            if isinstance(n, (int, float)) and isinstance(r, (int, float)):
                if abs(float(n) - float(r)) > float(i.get("tol") or 0.0):
                    mismatches.append(
                        {
                            "kind": i["kind"],
                            "nominal": n,
                            "readback": r,
                            "tol": i.get("tol"),
                        }
                    )
        version_ok = bool(self.model_config) and bool(self.model_revision)
        ok = not missing_kinds and not no_readback and not mismatches and version_ok
        return {
            "ok": ok,
            "missing_kinds": missing_kinds,
            "no_readback": no_readback,
            "mismatches": mismatches,
            "version_bound": version_ok,
            "mark": NOT_A_SAFETY_COMPLIANCE_STATEMENT,
            "reason": (
                "★ 尺寸/基准/公差都有回读，★ 且绑了配置 %r + 版本 %r"
                % (self.model_config, self.model_revision)
                if ok
                else "★★ 缺类 %r / 无回读 %r / 不符 %r / 版本未绑 %s"
                % (missing_kinds, no_readback, mismatches, not version_ok)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ EC08B 钣金（★ 展开一致性 + 折弯干涉）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class SheetMetalSpec:
    """★★ **钣金规格**（★ 逐字承 EC08B：★「★ 厚度/折弯半径/**工艺参数**、
    ★ **展开一致性**、**折弯干涉**、加工和装配空间」）。"""

    thickness_m: float = 0.0
    bend_radius_m: float = 0.0
    k_factor: float = 0.44
    #: ★ 折弯角度（★ 逐条）
    bends: list = field(default_factory=list)  #: `[{angle_deg, length_m}]`

    def radius_is_manufacturable(self) -> dict:
        """★★★ **折弯半径是否可制造**（★ 常见工艺下限：★ `R ≥ t`）。

        ★★ 依据（★ EC05 的 `mounting_bracket` 的 `failure_domain` 逐字：
          ★「★ **折弯半径 < 板厚**」是失败域）⇒ ★ 同口径。
        """
        if self.thickness_m <= 0:
            return {"ok": False, "reason": "★ 厚度必须为正"}
        ok = self.bend_radius_m >= self.thickness_m
        return {
            "ok": ok,
            "ratio": self.bend_radius_m / self.thickness_m,
            "reason": (
                "★ R/t = %.2f ≥ 1 ⇒ 可制造" % (self.bend_radius_m / self.thickness_m)
                if ok
                else "★★ R/t = %.2f < 1 ⇒ **折弯半径小于板厚**（★ 工艺不可行）"
                % (self.bend_radius_m / self.thickness_m)
            ),
        }

    def bend_allowance(self, angle_deg: float) -> float:
        """★ **折弯补偿**（★ 中性层弧长）：★ `BA = θ(rad) × (R + K·t)`。

        ★★ 依据（★ EC08B 逐字：★「★ 厚度/折弯半径/**工艺参数**」）——
          ★ K 因子是**工艺参数**。
        """
        theta = math.radians(abs(angle_deg))
        return theta * (self.bend_radius_m + self.k_factor * self.thickness_m)


def unfold_consistency(spec: SheetMetalSpec, *, flat_length_m: float) -> dict:
    """★★★★ **展开一致性**（★ 逐字承 EC08B：★「★ **展开一致性**」）。

    ★★ 判据：★ 展开长度必须等于 ★ **各段直线长 + 各折弯补偿**（★ 容差 1e-6 m）。
    """
    straight = sum(float(b.get("length_m") or 0.0) for b in spec.bends)
    allowance = sum(spec.bend_allowance(b.get("angle_deg") or 0.0) for b in spec.bends)
    expected = straight + allowance
    diff = abs(float(flat_length_m) - expected)
    return {
        "ok": diff <= 1e-6,
        "expected_m": expected,
        "actual_m": float(flat_length_m),
        "diff_m": diff,
        "bend_allowance_total_m": allowance,
        "reason": (
            "★ 展开长度与「直线 + 折弯补偿」一致（★ 差 %.2e m）" % diff
            if diff <= 1e-6
            else "★★ 展开长度 %.6f ≠ 期望 %.6f（★ 差 %.2e m）"
            % (flat_length_m, expected, diff)
        ),
    }


def bend_interference(spec: SheetMetalSpec, *, flange_heights_m: list) -> dict:
    """★★★★ **折弯干涉**（★ 逐字承 EC08B：★「★ **折弯干涉**」）。

    ★★ 判据（★ 常见工艺口径）：★ 相邻法兰的**净空**必须 ≥ ★ `R + t`（★ 否则折弯刀下不去）。
    """
    need = spec.bend_radius_m + spec.thickness_m
    bad = []
    for i, h in enumerate(flange_heights_m or []):
        if float(h) < need:
            bad.append({"index": i, "height_m": float(h), "need_m": need})
    return {
        "ok": not bad,
        "required_clearance_m": need,
        "interferences": bad,
        "reason": (
            "★ %d 个法兰净空都 ≥ R+t = %.4f" % (len(flange_heights_m or []), need)
            if not bad
            else "★★ %d 个法兰净空 < R+t ⇒ **折弯干涉**" % len(bad)
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ EC08C 焊件（★ 切割清单）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class WeldmentCutList:
    """★★ **焊件切割清单**（★ 逐字承 EC08C：★「★ 型材、连接、**切割清单**、
    ★ **焊接可达性**、变形与后加工假设」）。"""

    rows: list = field(default_factory=list)  #: `[{profile, length_m, qty, material}]`

    def add(
        self, profile: str, *, length_m: float, qty: int, material: str = ""
    ) -> None:
        self.rows.append(
            {
                "profile": profile,
                "length_m": float(length_m),
                "qty": int(qty),
                "material": material,
            }
        )

    def totals(self) -> dict:
        """★★★ **按型材汇总**（★ 逐字承 EC08C：★「★ **切割清单**」）。

        ★★ 判据：★ 同型材要**合并**（★ 那才是清单的意义）。
        """
        agg: dict = {}
        for r in self.rows:
            key = r["profile"]
            cur = agg.setdefault(
                key,
                {
                    "profile": key,
                    "total_length_m": 0.0,
                    "qty": 0,
                    "material": r.get("material", ""),
                },
            )
            cur["total_length_m"] += r["length_m"] * r["qty"]
            cur["qty"] += r["qty"]
        return {
            "ok": bool(agg),
            "by_profile": [agg[k] for k in sorted(agg)],
            "profiles": len(agg),
            "pieces": sum(r["qty"] for r in self.rows),
        }

    def weld_accessibility(self, *, joints: list) -> dict:
        """★★★★ **焊接可达性**（★ 逐字承 EC08C：★「★ **焊接可达性**」）。

        ★★ 判据：★ 每个接头必须有**可达的焊枪角度**（★ 0°~180° 之外不可达）。
        """
        bad = []
        for i, j in enumerate(joints or []):
            ang = float(j.get("torch_angle_deg") or 0.0)
            if not (0.0 <= ang <= 180.0):
                bad.append({"index": i, "angle_deg": ang})
        return {
            "ok": not bad,
            "joints": len(joints or []),
            "unreachable": bad,
            "reason": (
                "★ %d 个接头都可焊" % len(joints or [])
                if not bad
                else "★★ %d 个接头**焊枪不可达**" % len(bad)
            ),
        }


def cut_list_totals(rows: list) -> dict:
    """★ 对外入口（★ 与 `WeldmentCutList.totals()` 同义）。"""
    w = WeldmentCutList(rows=list(rows or []))
    return w.totals()


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ EC08D 曲面（★ 「看起来顺」不能当曲率通过）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class SurfaceContinuity:
    """★★★★★ **曲面连续性**（★ 逐字承 EC08D）：

    「★ 连续性、边界/拼接、偏差、厚化和工艺要求；★ **「看起来顺」不能当曲率通过**」。

    ★★★ **本类的意义**：★ 连续性**必须量**（★ `G0`/`G1`/`G2`），
      ★★ **不接受**「看着挺顺」这种话 ✗
    """

    patches: int = 0
    #: ★★ **每个接缝的连续性等级**（★ `G0` 位置 / `G1` 相切 / `G2` 曲率）
    seams: list = field(default_factory=list)  #: `[{between, level, deviation_mm}]`
    #: ★★ **最大偏差**（★ 厚化/拼接的偏差）
    max_deviation_mm: float = 0.0
    #: ★★ **最小厚度**（★ 厚化工艺要求）
    min_thickness_mm: float = 0.0

    def continuity_verdict(
        self, *, required: str = "G2", tolerance_mm: float = 0.05
    ) -> dict:
        """★★★ **连续性判定**（★ 逐条接缝都要达到要求等级）。

        ★★ 等级序：★ `G0` < `G1` < `G2`；★ 且**偏差必须 ≤ 容差**。
        """
        order = {"G0": 0, "G1": 1, "G2": 2}
        need = order.get(required, 2)
        bad = []
        for s in self.seams:
            lv = order.get(str(s.get("level")), -1)
            dev = float(s.get("deviation_mm") or 0.0)
            if lv < need or dev > tolerance_mm:
                bad.append(
                    {
                        "between": s.get("between"),
                        "level": s.get("level"),
                        "deviation_mm": dev,
                    }
                )
        if not self.seams:
            return {"ok": False, "reason": "★★ 一条接缝都没量 ⇒ 不算通过", "bad": []}
        return {
            "ok": not bad,
            "required": required,
            "tolerance_mm": tolerance_mm,
            "bad": bad,
            "reason": (
                "★ %d 条接缝都达 %s 且偏差 ≤ %.3f mm"
                % (len(self.seams), required, tolerance_mm)
                if not bad
                else "★★ %d 条接缝不达标" % len(bad)
            ),
        }

    def thicken_verdict(self, *, min_required_mm: float) -> dict:
        """★★ **厚化判定**（★ 逐字承 EC08D：★「★ ……**厚化**和工艺要求」）。"""
        ok = self.min_thickness_mm >= min_required_mm > 0
        return {
            "ok": ok,
            "min_thickness_mm": self.min_thickness_mm,
            "required_mm": min_required_mm,
            "reason": (
                "★ 最小厚度 %.3f ≥ %.3f ⇒ 可厚化"
                % (self.min_thickness_mm, min_required_mm)
                if ok
                else "★★ 最小厚度 %.3f < %.3f ⇒ **厚化会失败**"
                % (self.min_thickness_mm, min_required_mm)
            ),
        }


def surface_is_not_eyeballed(evidence: dict) -> dict:
    """★★★★★ **「看起来顺」不能当曲率通过**（★ 逐字承 EC08D）。

    ★★★ **判据**：★ 若只给了**视觉判断**（★ 如 `{"looks_smooth": True}`）而**没有量化读数**
      ⇒ ★ **不通过**（★ 记 `unknown`）✗
    """
    has_metric = any(
        k in (evidence or {})
        for k in ("seams", "max_deviation_mm", "min_thickness_mm", "curvature_error")
    )
    eyeballed = bool((evidence or {}).get("looks_smooth"))
    if not has_metric:
        return {
            "ok": False,
            "verdict": "unknown",
            "reason": (
                "★★★ 只有**视觉判断**（★ `looks_smooth=%r`）⇒ ★ "
                "**「看起来顺」不能当曲率通过**" % eyeballed
            ),
        }
    return {
        "ok": True,
        "verdict": "quantified",
        "reason": "★ 有**量化读数** ⇒ 可以判（★ 不是靠眼睛）",
    }
