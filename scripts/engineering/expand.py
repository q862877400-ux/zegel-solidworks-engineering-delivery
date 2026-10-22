"""★ 阶段 2 · 子方法展开 + 共享基准（规格 317 的 D1/D2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/expand.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D1（子方法展开）/ D2（共享基准）。★★ 
#           实测（2026-10-12）缺口：阶段 1 的 `resolve_step_name` 对`hole_group`（那是**
#           另一个方法 id**）给的是 `sub-method-not-expanded`⇒ ★ 而外部方案阶段 2 要求「
#           **子方法展开**」把它变成具体工具序列。
# 官方依据: 不适用（本仓自研编排层）。方法真源：`scripts/engineering/compiler.METHOD_LIB
#           RARY`名字真源：`scripts/engineering/registry.resolve_step_name`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage2_plate.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field

from . import registry as R

#: ★ 展开深度上限（★ J2：防循环）
MAX_DEPTH = 4


class ExpandError(Exception):
    """★ 展开失败（★ 带封闭码 —— 与 `RegistryError` 同族）。"""

    CODES = (
        "unknown-method",        #: ★ 方法 id 不在 METHOD_LIBRARY 里
        "depth-exceeded",        #: ★ 超展开深度（★ 可能循环）
        "empty-method",          #: ★ 方法没有步骤
        "unresolved-after-expand",  #: ★ 展开后仍有解析不到的步骤
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法展开拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、共享基准（★ D2）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DatumSpec:
    """★ 一个**具名基准**（★ 多步共用 —— ★ 改一处，引用它的步骤全改）。"""

    name: str
    role: str = "primary"          #: `primary` / `secondary`
    source_step: str = ""          #: ★ 哪个步骤建立它


def datum_index(steps) -> dict[str, list[int]]:
    """★ 基准名 → **引用它的步骤下标**（★ J5 的判据工具）。"""
    idx: dict[str, list[int]] = {}
    for i, st in enumerate(steps):
        for d in (getattr(st, "datums", ()) or ()):
            idx.setdefault(d, []).append(i)
    return idx


def rename_datum(steps, old: str, new: str) -> tuple:
    """★ 改基准名 ⇒ **所有引用它的步骤都改**（★ J5）。

    ★★ 为什么要有这个函数：手工改基准名必然漏（★ 本仓同族教训：
      「修了一个族」≠「修完了那个族」）。★ 这里由**索引**驱动，不会漏。
    """
    out = []
    for st in steps:
        ds = tuple(new if d == old else d for d in (getattr(st, "datums", ()) or ()))
        #: ★ `PlanStep` 是 frozen dataclass ⇒ 用 `replace` 语义重建
        kw = dict(step=st.step, params=dict(st.params), derive=st.derive, tool=st.tool)
        try:
            out.append(R.PlanStep(datums=ds, **kw))
        except TypeError:
            #: ★ 若 `PlanStep` 还没加 `datums` 字段 ⇒ 退回原样（★ 不静默丢）
            out.append(st)
    return tuple(out)


#: ══════════════════════════════════════════════════════════════════════
# 二、子方法展开（★ D1）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExpandedPlan:
    method_id: str
    steps: tuple = ()
    expand_trace: tuple = ()
    device_class: str = ""


def _methods() -> dict:
    from .compiler import METHOD_LIBRARY
    return METHOD_LIBRARY


def expand_plan(plan, reg: dict | None = None, *, max_depth: int = MAX_DEPTH) -> ExpandedPlan:
    """★ 把计划里**方法 id 形式的步骤**展开成工具序列（★ D1）。

    ★★ 展开规则（★ 唯一一条，不搞启发式 —— ★ 事实 53）：
       · 步骤名是**方法 id**  ⇒ 用 `METHOD_LIBRARY[id].steps` 替换
       · 步骤名是**工具裸名** ⇒ 保留

    ★★ 参数传递（★ J3）：子方法的步骤**继承父步骤的 `params`**（同名键透传）。
       ★ 例：`mounting_bracket` 的 `hole_group` 步骤带
         `params={"hole_diameter_mm": 6, "count": 4}` ⇒ 展开出的
         `sketch_add_circle` 拿到 `hole_diameter_mm`、`extrude_cut` 拿到 `count`。

    ★★ 递归（★ J1）：展开产物里**不得再有方法 id** —— 本函数循环到不动点为止。
    """
    reg = reg if reg is not None else R.build_registry()
    methods = _methods()
    trace: list[dict] = []

    def expand_one(steps, depth: int) -> list:
        if depth > max_depth:
            raise ExpandError(
                "depth-exceeded",
                "★ 展开深度超过 %d ⇒ 可能有**循环引用**（★ 不静默）" % max_depth)
        out: list = []
        for st in steps:
            name = getattr(st, "step", "")
            if name in methods:
                m = methods[name]
                sub = getattr(m, "steps", ()) or ()
                if not sub:
                    raise ExpandError("empty-method", "★ 方法 %r 没有步骤" % name)
                trace.append({"depth": depth, "expanded": name,
                              "into": list(sub),
                              "inherited_params": sorted(st.params)})
                #: ★ J3：子步骤继承父 `params`
                inherited = dict(st.params)
                kids = []
                for s in sub:
                    kw = dict(step=s, params=dict(inherited), derive=st.derive,
                              tool="")
                    try:
                        kids.append(R.PlanStep(datums=st.datums, **kw))
                    except TypeError:
                        kids.append(R.PlanStep(**kw))
                out.extend(expand_one(kids, depth + 1))
            else:
                out.append(st)
        return out

    steps = expand_one(list(getattr(plan, "steps", ()) or ()), 1)

    #: ★ J1：展开后**递归可解析**（★ 0 个方法 id 残留）
    left = [s.step for s in steps if getattr(s, "step", "") in methods]
    if left:
        raise ExpandError(
            "unresolved-after-expand",
            "★ 展开后仍有方法 id 残留：%s" % left)

    #: ★ 顺手解析工具名（★ 解析不到 ⇒ 抛 —— ★ 不静默）
    resolved = []
    for s in steps:
        cn = R.resolve_step_name(s.step, reg)
        resolved.append(R.PlanStep(step=s.step, params=dict(s.params),
                                   derive=s.derive, tool=cn))

    return ExpandedPlan(method_id=getattr(plan, "method_id", ""),
                        steps=tuple(resolved), expand_trace=tuple(trace),
                        device_class=getattr(plan, "device_class", ""))
