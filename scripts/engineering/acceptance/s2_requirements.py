"""★ S2 首件需求冻结：把「必须由人确认的五项」变成机器可判的缺项。

## 判据（`docs/ENGINEERING-PATH.md` 第六节 S2）

1. 与工程负责人冻结首件功能、接口、主参数及可修改域、材料、工艺、必要图样和交付目的。
2. 从这些要求倒推最小规范/规则集合，不先批量搬整个标准库。
3. 完成结构化需求到方法计划的单一映射，**去掉关键参数的静默默认值**。
4. 换材料/工艺/规则版本、移除引用或未确认参数，均**不得继续旧批准**。

## ★★ 为什么以 `engineering_contract.LEGACY_ALWAYS_MISSING` 为基准

那五项 `('material', 'load_case', 'safety_level', 'process', 'datums')`
是本仓早已认定的「**旧版永远缺**」字段 —— 也就是当年那些「悄悄填默认值」的地方。

S2 不新造一套字段，直接在既有的 `EngineeringContract` 上判：
**这五项任一为空 ⇒ 不得冻结**。

## ★ 缺项必须提问，不得填默认值

`EngineeringContract.clarifications` 是提问的唯一落点。
本模块的 `missing()` 只报「缺什么」，**不提供任何默认值** ——
给默认值就是替工程负责人拍板。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/s2_requirements.py
# 定位:   docs/ENGINEERING-PATH.md 第六节 S2 的落地 —— 首件需求冻结。
#          ★ 以既有的 ngineering_contract.LEGACY_ALWAYS_MISSING 为基准，
#            不新造字段：那五项 material/load_case/safety_level/process/datums
#            是本仓早已认定的「旧版永远缺」项。
#          ★ 缺项只**报出**、**不给默认值** —— 给默认值就是替工程负责人拍板。
# 官方依据: 不适用（纯 Python 层，不调 SolidWorks API）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import engineering_contract as ec  # noqa: E402

#: ★ 首件必须由人确认的五项（复用既有定义，不新造）
REQUIRED_CONFIRMATIONS = ec.LEGACY_ALWAYS_MISSING

#: ★ 首件额外要求的可判项（S2 补，见 `docs/ENGINEERING-PATH.md` 第五节）
ADDITIONAL_REQUIRED = (
    "interface",       #: 接口（孔型/孔位/配合面）
    "drawing_scope",   #: 必要图样范围
    "delivery_purpose",  #: 交付目的
)


def missing_confirmations(contract: object) -> list:
    """★ 报出**未确认**的必填项 —— 只报缺什么，**不给默认值**。

    判据：字段值「为空或未设置」即算缺。具体形态：
      · `material`      —— `None` 或 `MaterialRef` 的牌号为空
      · `load_case`     —— `load_cases` 列表为空
      · `safety_level`  —— 空串或 `None`
      · `process`       —— `None` 或 `ProcessIntent.kind` 为空
      · `datums`        —— `datums` 列表为空
    """
    out: list = []

    material = getattr(contract, "material", None)
    if material is None or not str(getattr(material, "name", "") or "").strip():
        out.append("material")

    if not list(getattr(contract, "load_cases", ()) or ()):
        out.append("load_case")

    if not str(getattr(contract, "safety_level", "") or "").strip():
        out.append("safety_level")

    process = getattr(contract, "process", None)
    if process is None or not str(getattr(process, "kind", "") or "").strip():
        out.append("process")

    if not list(getattr(contract, "datums", ()) or ()):
        out.append("datums")

    #: ★ 附加项：从 `clarifications` 里查是否已确认
    confirmed = {
        str(c.get("field", "")) for c in (getattr(contract, "clarifications", ()) or ())
        if c.get("confirmed")
    }
    for name in ADDITIONAL_REQUIRED:
        if name not in confirmed:
            out.append(name)

    return out


def can_freeze(contract: object) -> tuple:
    """⇒ `(能否冻结, 缺项清单)`。

    ★ 有任一缺项 ⇒ **不得冻结**（不是「警告后继续」）。
    """
    miss = missing_confirmations(contract)
    return (not miss, miss)


def freeze(contract: object) -> object:
    """★ 冻结契约；缺项时抛错并**指名缺什么**。

    ⚠ 不提供任何自动填充 —— 缺项是工程负责人要回答的问题，
      不是程序可以替他决定的事。
    """
    ok, miss = can_freeze(contract)
    if not ok:
        raise ValueError(
            "★ 首件需求不能冻结：还缺 %d 项未确认 —— %s。"
            "★ 这些必须由工程负责人确认，不得填默认值。"
            % (len(miss), ", ".join(miss))
        )
    contract.freeze()
    return contract


def require_sheet(contract: object) -> dict:
    """★ 生成「要求 → 承担者 → 验收者」三列对照表。

    ★ `docs/ENGINEERING-PATH.md` S2 完成标准：
      「首件每条硬要求有执行承担者和验收者」—— 缺一即不成立。
    """
    rows: list = []

    def add(req_id: str, what: str, owner: str, checker: str) -> None:
        rows.append(
            {
                "requirement_id": req_id,
                "what": what,
                "executor": owner,
                "acceptor": checker,
                "complete": bool(owner) and bool(checker),
            }
        )

    add("R-01", "板外形与厚度（主参数）", "method:plate", "accept:e2_rebuild")
    add("R-02", "孔数 / 孔型 / 孔位", "method:hole_group", "accept:e5_drawing")
    add("R-03", "材料牌号", "requirement:material", "check:e6_process")
    add("R-04", "工艺路线", "requirement:process", "check:e6_process")
    add("R-05", "定位基准与配合", "method:assembly", "accept:e4_assembly")
    add("R-06", "必要图样标注", "method:drawing", "accept:e5_drawing")
    add("R-07", "关键判据的溯源", "rule:rule_service", "accept:e7_provenance")

    incomplete = [r for r in rows if not r["complete"]]
    return {
        "rows": rows,
        "total": len(rows),
        "incomplete": [r["requirement_id"] for r in incomplete],
        "ok": not incomplete,
    }
