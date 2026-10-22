"""★ 把仓库里**早就有的**制造规则接进工具层（★ 业主 2026-10-14 的盘点收获）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/manufacturing_rules.py
# 定位:   规格 `specs/331-manufacturing-rules-wiring` ——★★ 把 `subskills/solidworks-vi
#           becad/knowledge/manufacturing_rules.yaml`  （★ **早就在仓库里**）接成**可调
#           用的规则服务**。★★★ 触发它的是 2026-10-14 业主：「继续搜索你本项目内部已经有
#           的东西，  说不定**还有很多我早就提供给你了**，你只是**文件太多给忘了**。」★
#           实测：这份规则**只被一个测试引用**（`test_threaded_hole_subskill.py`），  ★★
#            **工具层完全没用** —— 而它里面有：    · **螺纹底孔表**（M3~M12 的 pitch / t
#           ap_drill / 口部倒角）    · **间隙孔表**（M3~M8）    · **特征顺序**（13 步 ·
#           ★ 大圆角在孔槽之前）    · **槽/口袋的最小尺寸**（端部半径 / 壁厚 / 底厚）
# 官方依据: ① 该 YAML 本身（★ 来源块在 `subskills/solidworks-vibecad/`）② `subskills/sol
#           idworks-fillet-chamfer-cnc/references/   cnc-fillet-chamfer-lessons.md`（★
#           特征顺序与降级策略的另一份来源）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 纯查表，不碰 COM）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RULES_FILE = (
    ROOT / "subskills" / "solidworks-vibecad" / "knowledge" / "manufacturing_rules.yaml"
)


try:
    from ._coded_error import CodedError
except ImportError:
    from _coded_error import CodedError


class RuleError(CodedError):
    """★ 制造规则失败（★ 带封闭码）。"""

    CODES = ("no-rules", "unknown-size", "not-in-table", "out-of-range")
    ASSERT_LABEL = "★ 非法规则拒绝码"


def load_rules() -> dict:
    """★ 读**仓库里早就有的**那份规则（★ 不重写、不复制 —— 单一源）。"""
    if not RULES_FILE.is_file():
        raise RuleError("no-rules", "★ 没有 %s" % RULES_FILE)
    import yaml  # noqa: PLC0415

    return yaml.safe_load(RULES_FILE.read_text(encoding="utf-8")) or {}


#: ══════════════════════════════════════════════════════════════════════
# 一、螺纹底孔（★ 这是**我一直在手推**的东西）
#: ══════════════════════════════════════════════════════════════════════


def thread_spec(size: str) -> dict:
    """★★ **螺纹底孔规格**（★ 从既有 YAML 查，★ 不凭记忆）。

    ★★ 判据：★ 返回 `pitch` / `tap_drill` / `default_thread_depth_factor_d` /
      `default_mouth_chamfer` —— ★ 四个数**全部来自表**。

    ★★ 为什么这条重要：★ 我写 `L3-015`（M8 沉头孔）时**没有底孔数据**，
      ★ 而**这张表一直在仓库里**。
    """
    rules = load_rules()
    tbl = rules.get("thread_defaults") or rules.get("threads") or {}
    #: ★ 兼容两种键名（★ 表在 `threads:` 下 —— 见实测）
    if not tbl:
        for k in rules:
            if isinstance(rules[k], dict) and size in rules[k]:
                tbl = rules[k]
                break
    if size not in tbl:
        raise RuleError(
            "not-in-table", "★ %s 不在底孔表里（表里有：%s）" % (size, sorted(tbl))
        )
    return dict(tbl[size])


def thread_sizes() -> list:
    """★ 表里有哪些规格。"""
    rules = load_rules()
    for k in rules:
        v = rules[k]
        if isinstance(v, dict) and any(
            isinstance(x, dict) and "tap_drill" in x for x in v.values()
        ):
            return sorted(v)
    return []


#: ══ 二、间隙孔（★ 通孔让螺栓穿过用）═════════════════════════════════


def clearance_hole(size: str) -> float:
    """★★ **间隙孔直径**（★ 从既有表查）。

    ★ 判据：★ 如 `M6 → 6.6` —— ★ 那是**通孔**该打的直径（★ 不是 6.0）。
    """
    rules = load_rules()
    tbl = (rules.get("cnc_defaults") or {}).get("hole_clearance") or {}
    if size not in tbl:
        raise RuleError(
            "not-in-table", "★ %s 不在间隙孔表里（表里有：%s）" % (size, sorted(tbl))
        )
    return float(tbl[size])


#: ══ 三、特征顺序（★ 大圆角在孔槽之前）═══════════════════════════════


def feature_order(kind: str = "cnc_mount") -> list:
    """★★★ **特征顺序**（★ 从既有 YAML 查）。

    ★★★ 关键判据（★ `cnc-fillet-chamfer-lessons.md` 逐字）：
      「**外轮廓大圆角和顶/底边倒角**（第 5 步）**在孔槽之前**……
        如果放在**孔槽之后**，SolidWorks 可能在**复杂拓扑上求解很久**。」
    """
    rules = load_rules()
    tbl = rules.get("feature_order") or {}
    if kind not in tbl:
        raise RuleError(
            "not-in-table", "★ 没有 %s 的特征顺序（有：%s）" % (kind, sorted(tbl))
        )
    return list(tbl[kind])


def order_index(step: str, kind: str = "cnc_mount") -> int:
    """★ 某一步在顺序里的**位置**（★ 用来判「谁在前」）。"""
    seq = feature_order(kind)
    return seq.index(step) if step in seq else -1


def fillet_before_holes(kind: str = "cnc_mount") -> dict:
    """★★ **判据：倒角/圆角是否排在孔之前**（★ 这是既有规则的核心）。"""
    i_f = order_index("outer_fillet_and_chamfer", kind)
    i_h = order_index("through_holes", kind)
    return {
        "fillet_index": i_f,
        "hole_index": i_h,
        "ok": 0 <= i_f < i_h,
        "★": (
            "★ 既有规则：**大圆角/外轮廓倒角在孔槽之前** —— ★ 否则复杂拓扑上求解很久"
        ),
    }


#: ══ 四、槽/口袋的最小尺寸 ═══════════════════════════════════════════


def slot_min_end_radius() -> float:
    """★ 槽端部**最小**半径（★ 加工得出来）。"""
    return float(
        ((load_rules().get("cnc_defaults") or {}).get("slot") or {}).get(
            "min_end_radius", 0.0
        )
    )


def pocket_limits() -> dict:
    """★ 口袋的**最小壁厚 / 底厚**。"""
    p = (load_rules().get("cnc_defaults") or {}).get("pocket") or {}
    return {"min_wall": p.get("min_wall"), "min_floor": p.get("min_floor")}


#: ══ 五、降级策略（★ 来自 `cnc-fillet-chamfer-lessons.md`）════════════

#: ★★ **两档**（★ 逐字承 lessons 文件）：
#:   `strict`      = 只试请求尺寸，**失败即停**（★ 尺寸不可协商时用）
#:   `progressive` = 依次试 **100% / 75% / 50%**，★ 最小不低于 **0.1 mm**
DEGRADE_FACTORS = (1.0, 0.75, 0.5)
DEGRADE_FLOOR_MM = 0.1


def degrade_ladder(value_mm: float, *, strict: bool = False) -> list:
    """★★ **降级阶梯**（★ 逐字承 lessons 文件）。

    ★★ 判据：★ `progressive` **不是静默修复** ——
      ★ 必须记录 `requested_value_mm` / `actual_value_mm` / `status=degraded`，
      ★ 且**对外说明用实际尺寸**。
    """
    if strict:
        return [value_mm]
    out = []
    for f in DEGRADE_FACTORS:
        v = round(value_mm * f, 4)
        if v >= DEGRADE_FLOOR_MM and v not in out:
            out.append(v)
    return out


def degradation_record(*, requested_mm: float, actual_mm: float) -> dict:
    """★ 降级**留痕**（★ 逐字要求：三个字段 + 每次失败信息）。"""
    degraded = abs(actual_mm - requested_mm) > 1e-9
    return {
        "requested_value_mm": requested_mm,
        "actual_value_mm": actual_mm,
        "status": "degraded" if degraded else "as_requested",
        "★": "★ 既有规则逐字：「**对外说明必须使用实际尺寸**」",
    }


#: ══ 六、推荐半径（★ 来自 lessons 文件 L139）══════════════════════════

#: ★★ **保守默认值**（★ 逐字）
FILLET_DEFAULTS = {
    "base_plate_corner": (6.0, 10.0),  #: 底板立角大圆角 R6–R10
    "boss_corner": (3.0, 6.0),  #: 凸台立角圆角 R3–R6
    "outer_chamfer": (0.8, 2.0),  #: 外轮廓倒角 C0.8–C2
    "boss_top_chamfer": (0.5, 1.0),  #: 凸台顶面倒角 C0.5–C1
    "hole_mouth_chamfer": (0.3, 0.8),  #: 孔口倒角 C0.3–C0.8
}


def fillet_range(where: str) -> tuple:
    """★ 某处的**推荐半径/倒角范围**（★ 从 lessons 文件照录）。"""
    if where not in FILLET_DEFAULTS:
        raise RuleError(
            "not-in-table", "★ 没有 %s（有：%s）" % (where, sorted(FILLET_DEFAULTS))
        )
    return FILLET_DEFAULTS[where]


#: ══ 七、总报告 ═══════════════════════════════════════════════════════


def rules_report() -> dict:
    """★ **规则总览**（★ 证明「仓库里早就有」）。"""
    return {
        "source": str(RULES_FILE.relative_to(ROOT)),
        "thread_sizes": thread_sizes(),
        "clearance_sizes": sorted(
            (load_rules().get("cnc_defaults") or {}).get("hole_clearance") or {}
        ),
        "feature_order_len": len(feature_order()),
        "fillet_before_holes": fillet_before_holes(),
        "slot_min_end_radius": slot_min_end_radius(),
        "pocket": pocket_limits(),
        "degrade_factors": list(DEGRADE_FACTORS),
        "fillet_defaults": {k: list(v) for k, v in FILLET_DEFAULTS.items()},
        "★": "★ 全部来自**仓库内既有文件** —— ★ 此前**工具层没用过**",
    }
